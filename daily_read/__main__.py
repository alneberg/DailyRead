#!/usr/bin/env python
"""The Daily Read, a utility to generate and upload automatic progress reports for NGI Sweden."""

# Standard
import logging
import sys

# Installed
import click
from rich.logging import RichHandler

# Own
import daily_read.order_portal
import daily_read.daily_report
import daily_read.ngi_data

from daily_read import config_values


logging.basicConfig(
    level="INFO",
    format="%(message)s",
    handlers=[RichHandler()],
)

log = logging.getLogger(__name__)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def daily_read_cli():
    pass


def daily_read_safe_cli():
    try:
        daily_read_cli()
    except Exception as e:
        log.error(e)
        sys.exit(1)


### GENERATE ###
@daily_read_cli.group()
def generate():
    """Generate reports and save in a local git repository"""
    pass


@generate.command(name="all")
def generate_all():
    # Fetch data from all sources (configurable)
    sources = []
    if config_values.FETCH_FROM_NGIS:
        sources.append(daily_read.ngi_data.StockholmProjectData(config_values))
    if config_values.FETCH_FROM_SNPSEQ:
        sources.append(daily_read.ngi_data.SNPSEQProjectData(config_values))
    if config_values.FETCH_FROM_UGC:
        sources.append(daily_read.ngi_data.UGCProjectData(config_values))

    projects_data = daily_read.ngi_data.ProjectDataMaster(config_values, sources)

    log.info(f"Fetching data for {projects_data.source_names}")
    projects_data.get_data()
    log.info("Data fetched successfully")
    projects_data.save_data()
    log.info("Data saved to disk")

    modified_projects = projects_data.get_modified_projects()

    op = daily_read.order_portal.OrderPortal(config_values)
    op.get_orders()
    # TODO - not sure how to proceed, fetching ALL projects in order portal
    # and then generate reports seems quite slow and wasteful, but I haven't
    # tried so it might work. Maybe a pull model where we only generate reports
    # for projects that we know have been updated can be a better alternative?
    all_sthlm_orders = op.process_orders(use_node="Stockholm")
    # TODO: Should clean up...
    daily_rep = daily_read.daily_report.DailyReport(config_values.REPORTS_LOCATION)

    for owner in all_sthlm_orders:
        report = daily_rep.populate_and_write_report(owner, all_sthlm_orders[owner])
        for project in all_sthlm_orders[owner]["projects"]:
            op.upload_report_to_order_portal(report, project["iuid"])

        for project in all_sthlm_orders[owner]["projects"]:
            op.upload_report_to_order_portal(report, project["iuid"])


@generate.command(name="single")
@click.argument("orderer")
@click.option(
    "-l",
    "--location",
    type=click.Choice(["Stockholm", "Uppsala"], case_sensitive=False),
)
@click.option("-u", "--upload", is_flag=True, help="Trigger upload of reports.")
# TODO: is it possible to filter on orderer and location together in the API?
def generate_single(orderer, location, upload):
    log.info(f"Order portal URL: {config_values.ORDER_PORTAL_URL}")
    op = daily_read.order_portal.OrderPortal()
    op.get_orders(orderer=orderer, node=location)
    orders = op.process_orders(use_node=location)
    log.info(f"Found {len(orders)} order(s)")

    daily_rep = daily_read.daily_report.DailyReport()
    for owner in orders:
        report = daily_rep.populate_and_write_report(owner, orders[owner], config_values.REPORTS_LOCATION)
        for project in orders[owner]["projects"]:
            if upload:
                op.upload_report_to_order_portal(report, project["iuid"])


### UPLOAD ###
@daily_read_cli.group()
def upload():
    """Upload reports to the order portal"""
    pass


@upload.command(name="all")
def upload_all():
    pass


@upload.command(name="single")
@click.argument("orderer")
def upload_single(orderer):
    pass


@daily_read_cli.command()
def serve():
    """Starts a simple web server to display reports"""
    pass
