# The NGI Daily Read

A utility to generate and upload automatic progress reports for NGI Sweden.

## Planned Usage (yet to be implemented)

```bash
# Generate reports and save in a local git repository (location is given by configuration variable) and commit changes with a timestamp message
daily_read generate all

# Generate report for single orderer, need location specified, will not create git commit
daily_read generate single <ordererID> <location>

# the upload command 
daily_read upload all
daily_read upload single <orderer>

# Start a basic server to display all generated reports - NOT FOR PRODUCTION
daily_read serve --location
```

# Configuration variables

Configuration is dealt with via environment variables. Simplest way to set it up is to retrieve a `.env` file based on the `.env.example` provided in the repo. Environment variables which are not set have default variables in `daily_read/config.py`.

# Contributors

Johannes Alneberg
Anandashankar Anil
