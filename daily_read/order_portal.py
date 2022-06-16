"""Module to handle order portal interaction"""

from daily_read import config_values
import logging

log = logging.getLogger(__name__)

class OrderPortal(object):
    """Class to handle NGI order portal interaction"""

    def __init__(self):
        
        base_url = config_values.DAILY_READ_ORDER_PORTAL_URL
        api_key = config_values.DAILY_READ_ORDER_PORTAL_API_KEY

        if base_url is None:
            raise ValueError('environment variable DAILY_READ_ORDER_PORTAL_URL not set')

        if api_key is None:
            raise ValueError('Environment variable DAILY_READ_ORDER_PORTAL_API_KEY not set')

        self.base_url = base_url
        self.headers = {'X-OrderPortal-API-key': api_key}

