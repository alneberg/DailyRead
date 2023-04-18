"""Module to handle order portal interaction"""

# Standard
import base64
import datetime
import logging
from urllib.parse import urljoin

# installed
import requests

log = logging.getLogger(__name__)


class OrderPortal(object):
    """Class to handle NGI order portal interaction"""

    def __init__(self, config_values, projects_data):
        self.config_values = config_values
        base_url = config_values.ORDER_PORTAL_URL
        api_key = config_values.ORDER_PORTAL_API_KEY

        if base_url is None:
            raise ValueError("environment variable ORDER_PORTAL_URL not set")

        if api_key is None:
            raise ValueError("Environment variable ORDER_PORTAL_API_KEY not set")

        self.base_url = base_url
        self.headers = {"X-OrderPortal-API-key": api_key}
        self.projects_data = projects_data
        self.all_orders = []

    def _get(self, url, params):
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
        if not recent:
            # Fetch all orders
            params["year"] = "all"
        if orderer:
            params["owner"] = orderer

        response = self._get("api/v1/orders", params)

        try:
            self.all_orders = self.all_orders + response.json()["items"]
        except requests.exceptions.JSONDecodeError as e:
            log.critical(
                f"Could not fetch orders for {{node: {node}, status: {status}, orderer={orderer}, recent={recent}}}"
            )
            raise
        log.info(f"Fetched a total of {len(self.all_orders)} order(s) from the Order Portal")

    def process_orders(self, closed_before_in_days=30):
        """Process orderers orders to select ones that need to be updated"""

        order_updates = {}
        pull_date = datetime.datetime.now()
        older_than_cutoff = (pull_date - datetime.timedelta(days=closed_before_in_days)).date()
        for order in self.all_orders:
            if (
                order["status"] == "closed"
                and datetime.datetime.strptime(order["history"]["closed"], "%Y-%m-%d").date() >= older_than_cutoff
            ):
                continue
            if order["identifier"] in self.projects_data.data.keys():
                proj_info = self.projects_data.data[order["identifier"]]
                if order["reports"]:
                    proj_prog_rep = next(item for item in order["reports"] if item["name"] == "Project Progress")
                    proj_info.report_iuid = proj_prog_rep["iuid"]
                if proj_info.orderer in order_updates:
                    order_updates[proj_info.orderer]["projects"].append(proj_info)
                else:
                    order_updates[proj_info.orderer] = {
                        "pull_date": f"{pull_date}",
                        "projects": [proj_info],
                    }

        return order_updates

    def upload_report_to_order_portal(self, report, project):
        """Upload report to order portal"""
        add_to_url = ""
        if project.report_iuid:
            add_to_url = f"/{project.report_iuid}"
        url = f"{self.base_url}/api/v1/report{add_to_url}"
        indata = dict(
            order=project.project_id,
            name="Project Progress",
            status="published",
            file=dict(
                data=base64.b64encode(report.encode()).decode("utf-8"),
                filename="project_progress.html",
                content_type="text/html",
            ),
        )
        # TODO: check Encoded to utf-8 to display special characters properly
        response = requests.post(url, headers=self.headers, json=indata)

        assert response.status_code == 200, (response.status_code, response.reason)

        log.info(f"Updated report for order with project id: {project.project_id}")
