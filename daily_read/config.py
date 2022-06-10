import os

class Config(object):
    def __init__(self):
        self.DAILY_READ_ORDER_PORTAL_URL = os.getenv("DAILY_READ_ORDER_PORTAL_URL")
        self.DAILY_READ_ORDER_PORTAL_API_KEY = os.getenv("DAILY_READ_ORDER_PORTAL_API_KEY")
        self.DAILY_READ_REPORTS_LOCATION = os.getenv("DAILY_READ_REPORTS_LOCATION")
        self.DAILY_READ_NGIS_URL = os.getenv("DAILY_READ_NGIS_URL")
        self.DAILY_READ_SNPSEQ_URL = os.getenv("DAILY_READ_SNPSEQ_URL")