"""Module to generate daily reports"""

# Standard
import datetime
import logging
import os

# installed
import jinja2

log = logging.getLogger(__name__)


class DailyReport(object):
    """Class to handle daily report generation"""

    def __init__(self):
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("./daily_read/templates"))
        self.template = self.jinja_env.get_template("daily_report.html")

    def populate_and_write_report(self, pi_email, data, out_dir=None):
        """Populate report with values"""
        pull_date = f"{datetime.datetime.strptime(data['pull_date'], '%Y-%m-%d %H:%M:%S.%f').date()}"
        data["pull_date"] = pull_date
        filled_report = self.template.render(pi_email=pi_email, data=data)

        if out_dir:
            log.info(f"Writing reports into {out_dir}")
            file_name = os.path.join(out_dir, f"{pi_email.split('@')[0]}_{pull_date}.html")
            with open(file_name, mode="w", encoding="utf-8") as file:
                file.write(filled_report)
                log.debug(f"... wrote {file_name}")
        return filled_report
