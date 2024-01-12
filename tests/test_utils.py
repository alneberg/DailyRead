import logging
import pytest

from daily_read import utils


def test_error_reporting_without_error():
    """Test that no error is raised when log no has error messages"""
    daily_read_module_name = "daily_read.ngi_data"
    log = logging.getLogger(daily_read_module_name)
    log.info("Test info")
    log.warning("Warn message")
    try:
        utils.error_reporting(log)
    except RuntimeError:
        assert False, "This should not raise an exception"


def test_error_reporting_with_error():
    """Test error thrown when log has error messages"""
    daily_read_module_name = "daily_read.ngi_data"
    log = logging.getLogger(daily_read_module_name)
    log.error("Test error message")
    with pytest.raises(RuntimeError, match=f"Errors logged in {daily_read_module_name} during execution"):
        utils.error_reporting(log)
