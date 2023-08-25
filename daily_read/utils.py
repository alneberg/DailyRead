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
