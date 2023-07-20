"""Module to generate daily reports"""

# Standard
import datetime
import logging
import os
import sys
import subprocess

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

STATUS_DESCRIPTIONS = {
    "All Raw data Delivered": "The data has been made available through NGIs delivery system",
    "All Samples Sequenced": "Sequencing (including potential resequencing) of all samples has been finished",
    "Library QC finished": "Library QC is a quality control of the sequencing library produced either by NGI or supplied by you, depending on the type of project.",
    "Reception Control finished": "Reception Control consists of NGI staff measuring e.g. concentration and volume for the samples received.",
    "Samples Received": "The samples have been received and registered at NGI",
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
        git_commits = self.get_git_commits()
        filled_report = self.template.render(
            pi_email=pi_email,
            data=data,
            priority=priority,
            icons=STATUS_ICONS,
            portal_url=PORTAL_URL,
            status_desc=STATUS_DESCRIPTIONS,
            git_commits=git_commits,
        )

        if out_dir:
            file_name = os.path.join(out_dir, f"{pi_email.split('@')[0]}_{pull_date}.html")
            log.info(f"Writing report {file_name}")
            with open(file_name, mode="w", encoding="utf-8") as file:
                file.write(filled_report)
                log.debug(f"... wrote {file_name}")
        return filled_report

    def get_git_commits(self):
        git_commits = {}
        try:
            git_commits["git_commit"] = (
                subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"]).decode(sys.stdout.encoding).strip()
            )
            git_commits["git_commit_full"] = (
                subprocess.check_output(["git", "rev-parse", "HEAD"]).decode(sys.stdout.encoding).strip()
            )
        except:
            git_commits["git_commit"] = "unknown"
            git_commits["git_commit_full"] = "unknown"
        return git_commits
