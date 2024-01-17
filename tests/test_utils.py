import logging
import pytest

from daily_read import utils

daily_read_module_name = "tests"
log = logging.getLogger(daily_read_module_name)


def test_error_reporting_without_error():
    """Test that no error is raised when the log has no error messages"""
    log.info("Test info")
    log.warning("Warn message")
    try:
        utils.error_reporting(log, "tests")
    except RuntimeError:
        assert False, "This should not raise an exception"


def test_error_reporting_with_error():
    """Test error thrown when the log has error messages"""
    log.error("Test error message")
    with pytest.raises(RuntimeError, match=f"Errors logged in {daily_read_module_name} during execution"):
        utils.error_reporting(log, "tests")
