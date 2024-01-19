# The NGI Daily Read

[![codecov](https://codecov.io/gh/NationalGenomicsInfrastructure/DailyRead/graph/badge.svg?token=P3M4Y1N4SU)](https://codecov.io/gh/NationalGenomicsInfrastructure/DailyRead)

A utility to generate and upload automatic progress reports for NGI Sweden.

## How it works

- The script first fetches data from the appropriate NGI source, i.e. statusdb for Stockholm. Only projects with orders with a signed contract wil be fetched
- The data corresponding to each project will then be saved in a small data file (json, yaml or csv perhaps) on disk.
- Git will be used to track the directory where these files are kept (between runs of the script).
- Git status (inside python) will be used to check which projects has changes in their data since the last run and those projects will be selected.
- From the projects modified, a list of their associated orderers is created.
- For each unique orderer in the list, all projects are fetched from Order Portal. These are then filtered on the following criteria

  - All orders which are not in the data fetched from the NGI source are skipped.
  - All closed orders with close dates within 5 days of the cutoff date (default 30 days) will have their reports hidden.
  - All closed orders closed more than 5 days before the cutoff date are assumed to have their reports hidden and will be skipped.
  - All orders which are associated to a project NGI started to process but then aborted will have their reports hidden.

- A report with all active projects is generated for each unique orderer.
- Reports are uploaded to all orders accepted by NGI which have active projects or are marked to have their reports hidden.
- As each report is uploaded, the file of the corresponding project is staged for commit in the git repo.
- After all reports in the current run are uploaded, all staged files are committed in the git repo.
- The reports have timestamps which indicate when it was last updated
- If there are problems to upload to an order
  - Report to error log (cron will email this)
  - Do not stage these changes, will make sure that the orderer is re-tried next time.
  - Continue with next project

Also see diagram below:

![alt text](doc/figures/overview_dark.png#gh-dark-mode-only)
![alt text](doc/figures/overview_light.png#gh-light-mode-only)

## Usage

```bash
# Generate reports for all orderers and save them in a local directory. Project changes are saved in a local git repository (location is given by configuration variable) and committed with a timestamp message
daily_read generate all

# Generate and upload reports for all orderers to order portal. They will not be saved locally
daily_read generate all --upload

# Generate report for single orderer and save it to local directory
daily_read generate single --project <OrderID>

```

To generate and upload reports for a single user(or a list of users), their name(s) can be entered in a text file and provided to the environment variable `DAILY_READ_USERS_LIST_LOCATION`.

## Configuration variables

Configuration is dealt with via environment variables. Simplest way to set it up is to retrieve a `.env` file based on the `.env.example` provided in the repo. Environment variables which are not set have default variables in `daily_read/config.py`.

- `DAILY_READ_ORDER_PORTAL_URL` (str) : Order portal URL
- `DAILY_READ_ORDER_PORTAL_API_KEY` (str) : Order portal API key
- `DAILY_READ_REPORTS_LOCATION` (str) : Local disk location to save generated reports
- `DAILY_READ_DATA_LOCATION` (str) : Local disk location for data git repository
- `DAILY_READ_LOG_LOCATION` (str) : Local disk location to save log output
- `DAILY_READ_STHLM_STATUSDB_URL` (str) : NGI STHLM Data source URL
- `DAILY_READ_STHLM_STATUSDB_USERNAME` (str) : NGI STHLM Data source credentials
- `DAILY_READ_STHLM_STATUSDB_PASSWORD` (str) : NGI STHLM Data source credentials
- `DAILY_READ_FETCH_FROM_NGIS` (str) : Flag to turn on data fetching from NGI STHLM
- `DAILY_READ_SNPSEQ_URL` (str) : NGI STHLM Data source URL
- `DAILY_READ_USERS_LIST_LOCATION` (str) : Path on local disk to orderer list file (.txt) to send reports to, can be empty. The file would contain a single column of orderer email addresses.

## Developer note

### Formatting with Black and Prettier

This project is set up to use black and prettier to check code formatting. Please make sure these are enabled in your editor.
If you're having trouble getting prettier and black to work together, have a look at the following issue (with solution):
https://github.com/microsoft/vscode/issues/136179

### Getting prettier jinja plugin to work on VSCode

Prettier is not aware of jinja tags natively so we need a plugin [prettier-plugin-jinja-template](https://github.com/davidodenwald/prettier-plugin-jinja-template).
This is not available for install inside VSCode but one needs to install it manually (the version of the prettier extension might of course be different):

```zsh
cd ~/.vscode/extensions/esbenp.prettier-vscode-9.10.4
npm install
npm install --save-dev prettier prettier-plugin-jinja-template
```

Then remember to restart VSCode and it should work.

## Contributors

- Johannes Alneberg
- Anandashankar Anil
