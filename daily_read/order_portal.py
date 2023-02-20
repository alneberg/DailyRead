"""Module to handle order portal interaction"""

# Standard
import datetime
import logging
from urllib.parse import urljoin

# installed
import requests

from daily_read.utils import StatusdbSession

log = logging.getLogger(__name__)


class OrderPortal(object):
    """Class to handle NGI order portal interaction"""

    def __init__(self, config_values):
        self.config_values = config_values
        base_url = config_values.ORDER_PORTAL_URL
        api_key = config_values.ORDER_PORTAL_API_KEY

        if base_url is None:
            raise ValueError("environment variable ORDER_PORTAL_URL not set")

        if api_key is None:
            raise ValueError("Environment variable ORDER_PORTAL_API_KEY not set")

        self.base_url = base_url
        self.headers = {"X-OrderPortal-API-key": api_key}
        self.all_orders = None

    def __get(self, url, params):
        full_url = urljoin(self.base_url, url)

        return requests.get(full_url, headers=self.headers, params=params)

    def get_orders(self, node=None, status=None, orderer=None, recent=True):
        """recent==True would give only 500 most recent orders"""
        log.info("Fetching orders")
        params = {}
        if node:
            params["assigned_node"] = node
        if status:
            params["status"] = status
        if orderer is None:
            # Fetch all orders
            year = "all"
            if recent:
                year = "recent"
            params["year"] = year
            response = self.__get("/api/v1/orders", params)
        else:
            response = self.__get(f"/api/v1/account/{orderer}/orders", params)

        try:
            self.all_orders = response.json()["orders"]
        except requests.exceptions.JSONDecodeError as e:
            log.critical(
                f"Could not fetch orders for {{node: {node}, status: {status}, orderer={orderer}, recent={recent}}}"
            )
            raise
        log.info(f"Fetched {len(self.all_orders)} order(s) from the Order Portal")

    def process_orders(self, use_node="", closed_before_in_days=7):
        """process orders"""

        order_updates = {}
        pull_date = datetime.datetime.now()
        older_than_cutoff = (pull_date - datetime.timedelta(days=closed_before_in_days)).date()
        statusdb_sess = StatusdbSession(self.config_values, db="projects")
        for order in self.all_orders:
            process_order = True
            if use_node:
                process_order = order.get("fields", {}).get("assigned_node", "") == use_node

            if process_order:
                if (
                    order["status"] == "closed"
                    and datetime.datetime.strptime(order["history"]["closed"], "%Y-%m-%d").date() >= older_than_cutoff
                ):
                    continue
                proj_info = statusdb_sess.get_entry(order["identifier"])
                if proj_info:
                    proj_info[order["identifier"]]["pull_date"] = f"{pull_date}"
                    proj_info[order["identifier"]]["iuid"] = order["iuid"]
                    pi_email = order["owner"]["email"]
                    if pi_email in order_updates:
                        order_updates[pi_email]["projects"].append(proj_info[order["identifier"]])
                    else:
                        order_updates[pi_email] = {
                            "pull_date": f"{pull_date}",
                            "projects": [proj_info[order["identifier"]]],
                        }

        return order_updates

    def upload_report_to_order_portal(self, report, order_iuid):
        """Upload report to order portal"""

        url = f"{self.base_url}/api/v1/order/{order_iuid}/report"
        headers = {
            "X-OrderPortal-API-key": self.headers["X-OrderPortal-API-key"],
            "content-type": "text/html",
        }
        # Encoded to utf-8 to display special characters properly
        response = requests.put(url, headers=headers, data=report.encode("utf-8"))

        assert response.status_code == 200, (response.status_code, response.reason)

        log.info(f"Updated report for order with iuid: {order_iuid}")
