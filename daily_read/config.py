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

        self.DAILY_READ_ORDER_PORTAL_URL = os.getenv("DAILY_READ_ORDER_PORTAL_URL", conf["DAILY_READ_ORDER_PORTAL_URL"])
        self.DAILY_READ_ORDER_PORTAL_API_KEY = os.getenv(
            "DAILY_READ_ORDER_PORTAL_API_KEY", conf["DAILY_READ_ORDER_PORTAL_API_KEY"]
        )
        self.DAILY_READ_REPORTS_LOCATION = os.getenv("DAILY_READ_REPORTS_LOCATION", conf["DAILY_READ_REPORTS_LOCATION"])
        self.DAILY_READ_NGIS_URL = os.getenv("DAILY_READ_NGIS_URL")
        self.DAILY_READ_SNPSEQ_URL = os.getenv("DAILY_READ_SNPSEQ_URL")
        self.STHLM_STATUSDB_URL = os.getenv("STHLM_STATUSDB_URL", conf["STHLM_STATUSDB_URL"])
        self.STHLM_STATUSDB_USERNAME = os.getenv("STHLM_STATUSDB_USERNAME", conf["STHLM_STATUSDB_USERNAME"])
        self.STHLM_STATUSDB_PASSWORD = os.getenv("STHLM_STATUSDB_PASSWORD", conf["STHLM_STATUSDB_PASSWORD"])
