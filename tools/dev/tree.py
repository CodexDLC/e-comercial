from pathlib import Path


def print_tree(directory, prefix="", ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {".git", "__pycache__", ".venv", ".mypy_cache", ".idea", "data", "logs", "node_modules"}

    items = sorted([item for item in directory.iterdir() if item.name not in ignore_dirs])

    for i, item in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        print(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            new_prefix = prefix + ("    " if i == len(items) - 1 else "│   ")
            print_tree(item, new_prefix, ignore_dirs)


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    print(f"\033[1mProject Structure: {project_root.name}\033[0m")
    print_tree(project_root)
