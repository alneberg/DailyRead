import os
import yaml

from dotenv import load_dotenv


class Config(object):
    def __init__(self):

        load_dotenv()

        self.ORDER_PORTAL_URL = os.getenv("DAILY_READ_ORDER_PORTAL_URL")
        self.ORDER_PORTAL_API_KEY = os.getenv("DAILY_READ_ORDER_PORTAL_API_KEY")
        self.REPORTS_LOCATION = os.getenv("DAILY_READ_REPORTS_LOCATION")
        self.DATA_LOCATION = os.getenv("DAILY_READ_DATA_LOCATION")
        self.STHLM_STATUSDB_URL = os.getenv("DAILY_READ_STHLM_STATUSDB_URL")
        self.STHLM_STATUSDB_USERNAME = os.getenv("DAILY_READ_STHLM_STATUSDB_USERNAME")
        self.STHLM_STATUSDB_PASSWORD = os.getenv("DAILY_READ_STHLM_STATUSDB_PASSWORD")
        self.SNPSEQ_URL = os.getenv("DAILY_READ_SNPSEQ_URL")
