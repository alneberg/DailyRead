import logging
import pytest

from daily_read import utils


def test_error_reporting(caplog):
    """Test error thrown when log has error messages"""
    daily_read_module_name = "daily_read.ngi_data"
    log = logging.getLogger(daily_read_module_name)
    log.error("Test error message")
    with pytest.raises(RuntimeError, match=f"Errors logged in {daily_read_module_name} during execution"):
        utils.error_reporting(log)
