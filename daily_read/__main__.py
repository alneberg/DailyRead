#!/usr/bin/env python
"""The Daily Read, a utility to generate and upload automatic progress reports for NGI Sweden."""

# Standard
import datetime
import logging
import sys

# Installed
import click
from dateutil.relativedelta import relativedelta
import dotenv
from rich.logging import RichHandler

# Own
import daily_read.config
import daily_read.daily_report
import daily_read.ngi_data
import daily_read.order_portal


dotenv.load_dotenv()
config_values = daily_read.config.Config()


logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler()],
)

log = logging.getLogger(__name__)


STATUS_PRIORITY = {
    1: "Samples Received",
    2: "Reception Control finished",
    3: "Library QC finished",
    4: "All Samples Sequenced",
    5: "All Raw data Delivered",
}


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def daily_read_cli():
    pass


### GENERATE ###
@daily_read_cli.group()
def generate():
    """Generate reports and save in a local git repository"""
    pass


@generate.command(name="all")
@click.option("-u", "--upload", is_flag=True, help="Trigger upload of reports.")
@click.option("--develop", is_flag=True, help="Only generate max 5 reports, for dev purposes.")
def generate_all(upload=False, develop=False):
    # Fetch data from all sources (configurable)
    projects_data = daily_read.ngi_data.ProjectDataMaster(config_values)

    log.info(f"Fetching data for {projects_data.source_names}")
    projects_data.get_data()
    log.info("Data fetched successfully")
    projects_data.save_data()
    log.info("Data saved to disk")

    orderer_with_modified_projects = projects_data.find_unique_orderers()

    op = daily_read.order_portal.OrderPortal(config_values, projects_data=projects_data)
    nr_orderers = 0
    for orderer in orderer_with_modified_projects:
        if orderer:
            op.get_orders(orderer=orderer)
            nr_orderers += 1
        if nr_orderers > 4 and develop:
            break
    modified_orders = op.process_orders()
    daily_rep = daily_read.daily_report.DailyReport()

    for owner in modified_orders:
        if upload:
            report = daily_rep.populate_and_write_report(owner, modified_orders[owner], STATUS_PRIORITY)
            for project in modified_orders[owner]["projects"]:
                op.upload_report_to_order_portal(report, project)
        else:
            log.info("Saving report to disk instead of uploading")
            report = daily_rep.populate_and_write_report(
                owner, modified_orders[owner], STATUS_PRIORITY, out_dir=config_values.REPORTS_LOCATION
            )


@generate.command(
    name="single", help="Generate a report for a single project and save it locally. Mostly used for development"
)
@click.option(
    "-p",
    "--project",
    help="A project id to generate the report for.",
    type=str,
)
@click.option(
    "-o",
    "--include-older",
    help="Include projects that are older than 6 months.",
    is_flag=True,
)
def generate_single(project, include_older=False):
    projects_data = daily_read.ngi_data.ProjectDataMaster(config_values)
    # Fetch all projects so that the report will look the same
    log.info("Fetching data from NGI sources")
    if include_older:
        close_date = (datetime.datetime.now() - relativedelta(months=120)).strftime("%Y-%m-%d")
    else:
        close_date = None

    projects_data.get_data(close_date=close_date)

    op = daily_read.order_portal.OrderPortal(config_values, projects_data=projects_data)
    orderer = None
    for project_id, project_data in projects_data.data.items():
        if project_id == project:
            if project_data.orderer is None:
                log.error(f"Could not find orderer for project {project}")
                sys.exit(1)
            orderer = project_data.orderer
            break

    if orderer is None:
        log.error(f"Could not find project with id {project}")
        sys.exit(1)

    op.get_orders(orderer=orderer)
    filtered_orders = op.process_orders()
    daily_rep = daily_read.daily_report.DailyReport()

    for owner, owner_orders in filtered_orders.items():
        _ = daily_rep.populate_and_write_report(
            owner, owner_orders, STATUS_PRIORITY, out_dir=config_values.REPORTS_LOCATION
        )

    log.info(f"Wrote report to {config_values.REPORTS_LOCATION}")
