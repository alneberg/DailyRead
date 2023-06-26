"""Module to generate daily reports"""

# Standard
import datetime
import logging
import os

# installed
import jinja2

log = logging.getLogger(__name__)


STATUS_ICONS = {
    "All Raw data Delivered": "cloud-download",
    "All Samples Sequenced": "body-text",
    "Library QC finished": "check2-all",
    "Reception Control finished": "check2",
    "Samples Received": "box-seam",
}

PORTAL_URL = "https://ngisweden.scilifelab.se/orders"


class DailyReport(object):
    """Class to handle daily report generation"""

    def __init__(self):
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("./daily_read/templates"))
        self.template = self.jinja_env.get_template("daily_report.html.j2")

    def populate_and_write_report(self, pi_email, data, priority, out_dir=None):
        """Populate report with values"""
        pull_date = f"{datetime.datetime.strptime(data['pull_date'], '%Y-%m-%d %H:%M:%S.%f').date()}"
        data["pull_date"] = pull_date

        filled_report = self.template.render(
            pi_email=pi_email, data=data, priority=priority, icons=STATUS_ICONS, portal_url=PORTAL_URL
        )

        if out_dir:
            file_name = os.path.join(out_dir, f"{pi_email.split('@')[0]}_{pull_date}.html")
            log.info(f"Writing report {file_name}")
            with open(file_name, mode="w", encoding="utf-8") as file:
                file.write(filled_report)
                log.debug(f"... wrote {file_name}")
        return filled_report
