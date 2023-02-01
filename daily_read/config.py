import os
import yaml


class Config(object):
    def __init__(self, config_file):
        conf = {}
        try:
            with open(config_file, "r") as f:
                content = yaml.load(f, Loader=yaml.SafeLoader)
                conf.update(content)
        except IOError as e:
            pass

        self.ORDER_PORTAL_URL = os.getenv("DAILY_READ_ORDER_PORTAL_URL", conf.get("DAILY_READ_ORDER_PORTAL_URL"))
        self.ORDER_PORTAL_API_KEY = os.getenv(
            "DAILY_READ_ORDER_PORTAL_API_KEY", conf.get("DAILY_READ_ORDER_PORTAL_API_KEY")
        )
        self.REPORTS_LOCATION = os.getenv("DAILY_READ_REPORTS_LOCATION", conf.get("DAILY_READ_REPORTS_LOCATION"))
        self.DATA_LOCATION = os.getenv("DAILY_READ_DATA_LOCATION", conf.get("DAILY_READ_REPORTS_LOCATION"))
        self.STHLM_STATUSDB_URL = os.getenv("DAILY_READ_STHLM_STATUSDB_URL", conf.get("DAILY_READ_STHLM_STATUSDB_URL"))
        self.STHLM_STATUSDB_USERNAME = os.getenv(
            "DAILY_READ_STHLM_STATUSDB_USERNAME", conf.get("DAILY_READ_STHLM_STATUSDB_USERNAME")
        )
        self.STHLM_STATUSDB_PASSWORD = os.getenv(
            "DAILY_READ_STHLM_STATUSDB_PASSWORD", conf.get("DAILY_READ_STHLM_STATUSDB_PASSWORD")
        )
        self.SNPSEQ_URL = os.getenv("DAILY_READ_SNPSEQ_URL")
