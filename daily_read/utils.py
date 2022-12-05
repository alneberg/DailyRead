"""Classes for handling various utility functions"""

import couchdb
import logging

logger = logging.getLogger(__name__)

class StatusdbSession(object):
    """Wrapper class for couchdb."""
    def __init__(self, config, db=None):
        url_string = 'https://{}:{}@{}'.format(config.STHLM_STATUSDB_USERNAME, config.STHLM_STATUSDB_PASSWORD, config.STHLM_STATUSDB_URL)
        display_url_string = 'https://{}:{}@{}'.format(config.STHLM_STATUSDB_USERNAME, '*********', config.STHLM_STATUSDB_URL)
        self.connection = couchdb.Server(url=url_string)
        if not self.connection:
            raise Exception('Couchdb connection failed for url {}'.format(display_url_string))
        if db:
            self.db_connection = self.connection[db]

        self.projdates_view = self.db_connection.view('project/dailyread_dates')

    def get_entry(self, name):
        """Retrieve entry from a given db for a given name.

        :param name: unique name identifier (primary key, not the uuid)
        """
        view = self.projdates_view
        res = {k.key: k.value for k in view[name:f"{name}Z"]}
        return res
