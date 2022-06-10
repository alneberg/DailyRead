#!/usr/bin/env python
"""The Daily Read, a utility to generate and upload automatic progress reports for NGI Sweden."""

# Installed
import click
import logging

import daily_read
import daily_read.config

log = logging.getLogger()

config = daily_read.config.Config()

@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def daily_read_cli():
    pass

@daily_read_cli.command()
def generate():
    """Generate reports and save in a local git repository"""
    print(config.DAILY_READ_ORDER_PORTAL_URL)


@daily_read_cli.command()
def upload():
    """Upload reports to the order portal"""
    pass

@daily_read_cli.command()
def serve():
    """Starts a simple web server to display reports"""
    pass