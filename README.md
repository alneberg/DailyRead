# The NGI Daily Read

A utility to generate and upload automatic progress reports for NGI Sweden.

## Suggested logic

* The script first fetches data from the appropriate NGI source, i.e. statusdb for Stockholm.
* The data corresponding to each project will then be saved in a small data file (json, yaml or csv perhaps) on disk.
* Git will be used to track the directory where these files are kept (between runs of the script).
* Git status (inside python) will be used to check which projects has changes in their data since the last run and those projects will be selected.
* For each orderer, fetch all their recent projects from Order Portal. A report will be generated with potentially several projects.
* Reports are uploaded to each project.
* We need to make sure the reports are transparent about timestamps when it was last updated  - Javascript?
* If problems to upload to a project?
  * Report to error log (cron will email this)
  * Do not stage these changes, will make sure that the orderer is re-tried next time.
  * Continue with next project

Also see diagram below:

![alt text](doc/figures/overview_dark.png#gh-dark-mode-only)
![alt text](doc/figures/overview_light.png#gh-light-mode-only)

## Planned Usage (yet to be implemented)

```bash
# Generate reports and save in a local git repository (location is given by configuration variable) and commit changes with a timestamp message
daily_read generate all

# Generate report for single orderer, need location specified, will not create git commit
daily_read generate single <ordererID> <location>

# Generate and upload
daily_read generate all --upload
daily_read generate single <orderer>

```

## Configuration variables

Configuration is dealt with via environment variables. Simplest way to set it up is to retrieve a `.env` file based on the `.env.example` provided in the repo. Environment variables which are not set have default variables in `daily_read/config.py`.

## Developer note

### Formatting with Black and Prettier

This project is set up to use black and prettier to check code formatting. Please make sure these are enabled in your editor.

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

* Johannes Alneberg
* Anandashankar Anil
