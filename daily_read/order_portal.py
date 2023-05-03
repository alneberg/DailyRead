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

        # Add trailing / for urljoin to parse order portal url properly
        if not base_url.endswith("/"):
            base_url = f"{base_url}/"

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

        dates_prio = {
            "All Raw data Delivered": 5,
            "All Samples Sequenced": 4,
            "Library QC finished": 3,
            "Reception Control finished": 2,
            "Samples Received": 1,
            "None": 0,
        }

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
                    prog_reports = [item for item in order["reports"] if item["name"] == "Project Progress"]
                    if len(prog_reports) > 1:
                        log.error(f"Multiple reports for Project Progress for order {order['identifier']}")
                    else:
                        proj_info.report_iuid = prog_reports[0]["iuid"]

                if proj_info.orderer not in order_updates:
                    order_updates[proj_info.orderer] = {
                        "pull_date": f"{pull_date}",
                        "active_projects": 0,
                        "recents": {},
                        "projects": {},
                    }

                latest_date = "0000-00-00"
                latest_status = "None"
                for date_value in proj_info.data["proj_dates"]:
                    date_statuses = proj_info.data["proj_dates"][date_value]
                    # Activity on 5 recent dates
                    recents_keys = sorted(order_updates[proj_info.orderer]["recents"].keys())
                    if len(recents_keys) < 5:
                        for status in date_statuses:
                            order_updates[proj_info.orderer]["recents"].setdefault(date_value, []).append(
                                (proj_info.data["project_name"], status)
                            )
                    else:
                        if date_value > recents_keys[0]:
                            order_updates[proj_info.orderer]["recents"].pop(recents_keys[0])
                            for status in date_statuses:
                                order_updates[proj_info.orderer]["recents"].setdefault(date_value, []).append(
                                    (proj_info.data["project_name"], status)
                                )

                    # Find status
                    if date_value > latest_date:
                        latest_date = date_value
                        for status in date_statuses:
                            if dates_prio[status] > dates_prio[latest_status]:
                                latest_status = status

                order_updates[proj_info.orderer]["projects"].setdefault(latest_status, []).append(proj_info)
                order_updates[proj_info.orderer]["active_projects"] += 1
        return order_updates

    def upload_report_to_order_portal(self, report, project):
        """Upload report to order portal"""
        # Encoded to utf-8 to display special characters properly
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
