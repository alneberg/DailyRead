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

        order_updates = {}
        pull_date = datetime.datetime.now()
        older_than_cutoff = (pull_date - datetime.timedelta(days=closed_before_in_days)).date()
        for order in self.all_orders:
            # Skip projects closed some time ago or if data is not available
            if (
                order["status"] == "closed"
                and datetime.datetime.strptime(order["history"]["closed"], "%Y-%m-%d").date() >= older_than_cutoff
            ):
                continue
            elif order["identifier"] not in self.projects_data.data.keys():
                log.debug(f"Order portal id: {order['identifier']} not found in data fetched form sources")
                continue

            proj_info = self.projects_data.data[order["identifier"]]
            if order["reports"]:
                prog_reports = [item for item in order["reports"] if item["name"] == "Project Progress"]
                if prog_reports:
                    if len(prog_reports) == 1:
                        proj_info.report_iuid = prog_reports[0]["iuid"]
                    else:
                        raise ValueError(
                            f"Multiple reports for Project Progress found in the Order Portal for order {order['identifier']}"
                        )

            if proj_info.orderer not in order_updates:
                order_updates[proj_info.orderer] = {
                    "pull_date": f"{pull_date}",
                    "active_projects": 0,
                    "recents": {},
                    "events": [],
                    "projects": {},
                }

            order_updates_item = order_updates[proj_info.orderer]
            order_updates_item["events"] += proj_info.events

            # Sort the statuses based on date and extract the 5 first (done repeatedly for each new project added)
            orderer_recents = dict(sorted(order_updates_item["events"], reverse=True)[:5])

            order_updates_item["recents"] = orderer_recents
            order_updates_item["projects"].setdefault(proj_info.status, []).append(proj_info)
            order_updates_item["active_projects"] += 1

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
