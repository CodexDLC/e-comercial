"""Unit tests for the logging settings adapter."""

import sys
from pathlib import Path

import pytest
from django.test import override_settings

from core.logger import DjangoLoggingSettingsAdapter

pytestmark = pytest.mark.unit

# Use a platform-appropriate absolute path so the test runs on both Linux and Windows.
_ABS_LOG_DIR = "C:\\tmp\\hop-and-barley-logs" if sys.platform == "win32" else "/tmp/hop-and-barley-logs"


@override_settings(LOG_DIR="logs")
def test_logging_adapter_resolves_relative_log_dir(settings):
    adapter = DjangoLoggingSettingsAdapter()
    assert Path(adapter.log_dir) == Path(settings.BASE_DIR) / "logs"


@override_settings(LOG_DIR=_ABS_LOG_DIR)
def test_logging_adapter_keeps_absolute_log_dir():
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.log_dir == _ABS_LOG_DIR


@override_settings(LOG_LEVEL_CONSOLE="DEBUG", LOG_LEVEL_FILE="WARNING")
def test_logging_adapter_reads_log_levels():
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.log_level_console == "DEBUG"
    assert adapter.log_level_file == "WARNING"


@override_settings(LOG_ROTATION="50 MB")
def test_logging_adapter_reads_log_rotation():
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.log_rotation == "50 MB"


@override_settings(DEBUG=True)
def test_logging_adapter_debug_flag():
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.debug is True


@override_settings(DEBUG=False)
def test_logging_adapter_debug_false():
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.debug is False


def test_logging_adapter_uses_defaults_when_settings_missing():
    """Adapter must not crash if optional settings are absent."""
    adapter = DjangoLoggingSettingsAdapter()
    assert adapter.log_level_console is not None
    assert adapter.log_level_file is not None
    assert adapter.log_rotation is not None
