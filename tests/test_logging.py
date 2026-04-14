import pytest
from pathlib import Path

pytestmark = pytest.mark.unit

from django.test import override_settings

from core.logger import DjangoLoggingSettingsAdapter


@override_settings(LOG_DIR="logs")
def test_logging_adapter_resolves_relative_log_dir(settings):
    adapter = DjangoLoggingSettingsAdapter()

    assert Path(adapter.log_dir) == Path(settings.BASE_DIR) / "logs"


@override_settings(LOG_DIR="/tmp/hop-and-barley-logs")
def test_logging_adapter_keeps_absolute_log_dir():
    adapter = DjangoLoggingSettingsAdapter()

    # Use path-agnostic comparison for Windows/POSIX paths
    assert Path(adapter.log_dir).as_posix().endswith("/tmp/hop-and-barley-logs")
