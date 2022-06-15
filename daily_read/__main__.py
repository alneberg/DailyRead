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

### GENERATE ###
@daily_read_cli.group()
def generate():
    """Generate reports and save in a local git repository"""
    pass

@generate.command(name='all')
def generate_all():
    pass

@generate.command(name='single')
@click.argument('orderer')
@click.argument('location')
def generate_single():
    pass

### UPLOAD ###
@daily_read_cli.group()
def upload():
    """Upload reports to the order portal"""
    pass

@upload.command(name='all')
def upload_all():
    pass

@upload.command(name='single')
@click.argument('orderer')
def upload_single(orderer):
    pass

@daily_read_cli.command()
def serve():
    """Starts a simple web server to display reports"""
    pass