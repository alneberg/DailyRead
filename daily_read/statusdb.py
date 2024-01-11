"""Classes for handling various utility functions"""


import logging

import couchdb

log = logging.getLogger(__name__)


class StatusDBSession(object):
    def __init__(self, config):
        url_string = (
            f"https://{config.STHLM_STATUSDB_USERNAME}:{config.STHLM_STATUSDB_PASSWORD}@{config.STHLM_STATUSDB_URL}"
        )
        display_url_string = f"https://{config.STHLM_STATUSDB_USERNAME}:*********@{config.STHLM_STATUSDB_URL}"
        self.connection = couchdb.Server(url=url_string)
        if not self.connection:
            raise ConnectionError(f"Couchdb connection failed for url {display_url_string}")
        self.db_connection = self.connection["projects"]

        self.projdates_view = self.db_connection.view(
            "project/dailyread_dates",
        )

    def rows(self, close_date=None):
        view = self.db_connection.view("project/dailyread_dates", descending=True, endkey=[close_date, "ZZZZ"])
        return view.rows
