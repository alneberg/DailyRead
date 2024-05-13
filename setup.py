from setuptools import setup, find_packages

from daily_read import __version__

with open("README.md") as f:
    readme = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="Daily Read",
    version=__version__,
    description="A utility to generate and upload automatic progress reports for NGI Sweden.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=[
        "biology",
        "sequencing",
        "NGS",
        "next generation sequencing",
    ],
    author="Johannes Alneberg",
    author_email="johannes.alneberg@scilifelab.se",
    url="https://github.com/NationalGenomicsInfrastructure/DailyRead",
    license="MIT",
    entry_points={"console_scripts": ["daily_read=daily_read.__main__:daily_read_cli"]},
    install_requires=required,
    packages=find_packages(exclude=("docs")),
    include_package_data=True,
    zip_safe=False,
)
