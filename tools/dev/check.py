"""Quality gate for Hop-and-Barley."""

import json
import os
import sys
import time
from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner, Colors

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent.parent
COMPOSE_FILE = PROJECT_ROOT / "deploy" / "docker-compose.test.yml"
TEST_PROJECT_NAME = "hop-and-barley-quality-check"
E2E_BASE_URL = "http://localhost:8001"


class CheckRunner(BaseCheckRunner):
    """Quality gate runner with Docker validation and E2E smoke tests."""

    def docker_compose(self, args: str) -> tuple[bool, str]:
        env = os.environ.copy()
        env["CONTAINER_PREFIX"] = TEST_PROJECT_NAME
        cmd = f"docker compose -p {TEST_PROJECT_NAME} -f {COMPOSE_FILE} {args}"
        return self.run_command(cmd, env=env)

    def cleanup_docker(self) -> None:
        print(f"\n{Colors.BLUE}🧹 Cleaning up Docker resources (Project: {TEST_PROJECT_NAME})...{Colors.ENDC}")
        self.docker_compose("down -v")
        self.run_command("docker volume prune -f")

    def run_docker_validation(self, ci_mode: bool = False) -> bool:
        self.print_step(f"Docker Validation (project: {TEST_PROJECT_NAME})")

        # Verify Docker daemon is running
        success, _ = self.run_command("docker info", capture_output=True)
        if not success:
            self.print_error("Docker is not running. Please start Docker Desktop.")
            return False

        if not COMPOSE_FILE.exists():
            self.print_error(f"Compose file not found at {COMPOSE_FILE}")
            return False

        # Clean slate
        self.cleanup_docker()

        try:
            self.print_step("Building Docker images (no-cache)")
            if not self.docker_compose("build --no-cache")[0]:
                return False

            self.print_step("Starting containers")
            if not self.docker_compose("up -d")[0]:
                return False

            # Wait for services to be ready with polling
            max_wait = 300
            start_time = time.time()
            self.print_step(f"Waiting for services to be ready (max {max_wait}s)")

            all_ready = False
            while time.time() - start_time < max_wait:
                ok, ps_out = self.docker_compose("ps --format json")
                if not ok or not ps_out:
                    time.sleep(2)
                    continue

                try:
                    containers: list[dict[str, object]] = []
                    for line in ps_out.strip().split("\n"):
                        line = line.strip()
                        if not line or not (line.startswith("{") or line.startswith("[")):
                            continue
                        try:
                            data = json.loads(line)
                            containers.extend(data if isinstance(data, list) else [data])
                        except json.JSONDecodeError:
                            continue

                    if not containers:
                        if int(time.time() - start_time) % 10 == 0:
                            print(f"  ...no containers found yet for project {TEST_PROJECT_NAME}")
                        time.sleep(2)
                        continue

                    current_failed = []
                    container_details = []
                    for c in containers:
                        state = str(c.get("State", "")).lower()
                        health = str(c.get("Health", "")).lower()
                        service = str(c.get("Service", "unknown"))
                        
                        container_details.append(f"{service}({state}/{health if health else 'no-hc'})")

                        # If a container is restarting, it usually means it crashed
                        if "restarting" in state:
                            self.print_error(f"Service {service} is restarting (likely crashed)")
                            _, logs = self.docker_compose(f"logs --tail=50 {service}")
                            print(f"\n{Colors.CYAN}Logs for {service}:{Colors.ENDC}")
                            print(logs)
                            return False

                        # We consider it ready ONLY if it's running AND (if it has healthcheck, it's healthy)
                        is_ready = ("running" in state)
                        if health and health != "healthy":
                            is_ready = False
                        
                        if not is_ready:
                            current_failed.append(service)

                    if int(time.time() - start_time) % 10 == 0:
                        print(f"  ...waiting for: {', '.join(current_failed)} (Checked: {', '.join(container_details)})")

                    if not current_failed:
                        self.print_success("All containers are running/healthy")
                        all_ready = True
                        break
                except Exception as e:
                    if int(time.time() - start_time) % 10 == 0:
                        print(f"{Colors.YELLOW}Warning: error during health check: {e}{Colors.ENDC}")

                time.sleep(2)

            if not all_ready:
                self.print_error(f"Timeout waiting for services after {max_wait}s")
                # Diagnostic dump
                _, ps_out = self.docker_compose("ps --format json")
                print(f"{Colors.YELLOW}Final container states:{Colors.ENDC}")
                print(ps_out)
                return False

            # Resolve the backend container ID (must use capture_output=True)
            env = os.environ.copy()
            env["CONTAINER_PREFIX"] = TEST_PROJECT_NAME
            _, cid = self.run_command(
                f"docker compose -p {TEST_PROJECT_NAME} -f {COMPOSE_FILE} ps -q backend",
                capture_output=True,
                env=env,
            )
            container_id = cid.strip() if cid else None
            if not container_id:
                self.print_error("Backend container not found")
                return False

            # Verify the backend process is running
            self.print_step("Checking backend process")
            success, ps_out = self.run_command(f"docker exec {container_id} ps aux", capture_output=True)
            if not any(x in ps_out for x in ["manage.py", "gunicorn"]):
                self.print_error("Backend process (gunicorn/manage.py) not found in container")
                return False

            # Run Django management checks inside the container
            backend_checks = [
                ("Django system check", "python manage.py check"),
                ("Migration plan", "python manage.py showmigrations --plan"),
            ]

            for desc, cmd in backend_checks:
                self.print_step(f"Docker | {desc}")
                success, out = self.run_command(
                    f"docker exec {container_id} {cmd}", capture_output=True
                )
                if not success:
                    self.print_error(f"{desc} failed:\n{out}")
                    return False
                self.print_success(f"{desc} passed")

            # Run E2E smoke tests (HTTP requests against the running stack)
            self.print_step("E2E smoke tests (HTTP against running containers)")
            python = sys.executable
            e2e_env = os.environ.copy()
            e2e_env["E2E_BASE_URL"] = E2E_BASE_URL
            e2e_cmd = (
                f"{python} -m pytest tests/e2e/ -m e2e -v --no-header "
                f"--override-ini=addopts='' "
                f"-p no:warnings"
            )
            ok, out = self.run_command(
                e2e_cmd, env=e2e_env, capture_output=ci_mode
            )
            if not ok:
                self.print_error(f"E2E smoke tests failed:\n{out}")
                return False
            self.print_success("E2E smoke tests passed")

            return True

        finally:
            self.cleanup_docker()

    def extra_checks(self) -> bool:
        """Run standard extra checks then optionally run Docker + E2E validation."""
        if not super().extra_checks():
            return False

        ci_mode = "--ci" in sys.argv
        if ci_mode:
            return self.run_docker_validation(ci_mode=True)

        try:
            prompt = (
                f"\n{Colors.YELLOW}"
                f"🚀 Run Docker validation + E2E smoke tests? [y/N]: "
                f"{Colors.ENDC}"
            )
            answer = input(prompt).strip().lower()
        except EOFError:
            answer = "n"

        if answer == "y":
            return self.run_docker_validation(ci_mode=False)

        self.print_skip("Skipping Docker validation.")
        return True


    def run_all(self) -> None:
        """Run checks in optimal order for developer feedback:
        Quality (fastest) → Unit Tests → Types → Security → Integration → Docker (slowest).
        """
        os.system("cls" if os.name == "nt" else "clear")

        if not self.check_quality():
            sys.exit(1)

        # Unit tests run automatically and fast (no external services)
        self.print_step("Unit Tests")
        if not self._run_auto_test_stages():
            sys.exit(1)

        if not self.check_types():
            sys.exit(1)
        if not self.check_security():
            sys.exit(1)

        # Integration tests are prompted (require real DB/Redis)
        if not self._run_prompted_test_stages():
            sys.exit(1)

        # Docker validation + E2E smoke tests are always last (slowest)
        # This only runs if quality/unit/types/security/integration tests pass.
        if not self.extra_checks():
            sys.exit(1)

        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED!{Colors.ENDC}")

        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED!{Colors.ENDC}")


def main() -> None:
    """Run the quality gate."""
    root = Path(__file__).parent.parent.parent
    CheckRunner(root).main()


if __name__ == "__main__":
    main()
