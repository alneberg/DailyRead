"""Module to generate daily reports"""

# Standard
import datetime
import logging
import os

# installed
import jinja2

from daily_read import templates

log = logging.getLogger(__name__)


class DailyReport(object):
    """Class to handle daily report generation"""

    def __init__(self, out_dir):
        ##Correct this
        templates_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "templates")
        )
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir)
        )
        self.template = self.jinja_env.get_template("daily_report.html")

    def populate_and_write_report(self, pi_email, data, out_dir=None):
        """Populate report with values"""

        pull_date = f"{datetime.datetime.strptime(data['pull_date'], '%Y-%m-%d %H:%M:%S.%f').date()}"
        data["pull_date"] = pull_date
        import pdb

        pdb.set_trace()
        filled_report = self.template.render(pi_email=pi_email, data=data)
        if out_dir:
            file_name = os.path.join(
                out_dir, f"{pi_email.split('@')[0]}_{pull_date}.html"
            )
            with open(file_name, mode="w", encoding="utf-8") as file:
                file.write(filled_report)
                log.info(f"... wrote {filename}")
        return filled_report
