"""Module to handle order portal interaction"""

# Standard
import logging

# installed
import requests

from daily_read import config_values

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
        self.all_orders = None


    def __get(self, url, params):
        full_url = f"{self.base_url}/{url}"
        return requests.get(full_url, headers=self.headers, params=params)

    def get_orders(self, orderer=None, recent=True):
        """recent==True would give only 500 most recent orders"""
        if orderer is None:
            # Fetch all orders
            response = self.__get('orders/api/v1/orders', params={'recent': recent})
            self.all_orders = response.json()
        else:
            # Not yet implemented in orderportal api
            pass