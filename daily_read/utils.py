"""Module for common utility functions"""

import logging
import subprocess
import sys


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.

    """

    def filter(self, record):
        """Inject commit_id into the log"""
        record.commit = get_git_commits()["git_commit"]
        return True


def get_git_commits():
    git_commits = {}
    try:
        git_commits["git_commit"] = (
            subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"]).decode(sys.stdout.encoding).strip()
        )
        git_commits["git_commit_full"] = (
            subprocess.check_output(["git", "rev-parse", "HEAD"]).decode(sys.stdout.encoding).strip()
        )
    except:
        git_commits["git_commit"] = "unknown"
        git_commits["git_commit_full"] = "unknown"
    return git_commits


# Rudimentary Error reporting
def error_reporting(log, module="all"):
    """Raise an error if there are Error level messages in the daily_read module logs"""
    error_string = ""
    if module == "all":
        module = "daily_read"
    for child in log.root.manager.loggerDict:
        if module in child:
            cache = log.root.getChild(child)._cache
            # If there are errors messages in the log, the cache will have the element 40: True
            if 40 in cache and cache[40]:
                error_string += f"\nErrors logged in {child} during execution"
    if error_string:
        sys.tracebacklimit = 0
        raise RuntimeError(error_string)
