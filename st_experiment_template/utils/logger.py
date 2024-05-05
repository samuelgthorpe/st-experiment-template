"""
Module to house logging tools.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import sys
import os
import platform
import sysconfig
from os.path import basename
import logging
import git
import pkg_resources
import pytz
from datetime import datetime
import time
from st_experiment_template import BASE_DIR


# # Globals
# -----------------------------------------------------|
run_dir = os.path.join(BASE_DIR, 'run')
log_dir = os.path.join(run_dir, 'logs')


# # Primary init log method
# -----------------------------------------------------|
def init_log(console_level="INFO", file_level="INFO", **kwrgs):
    """Initialize logger.

    Args:
        console_level (str, optional): console logging level, e.g. WARNING
        file_level (str, optional): file logging level, e.g. DEBUG
        **kwrgs: Description

    Returns:
        root logger
    """
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    _setup_record_factory()

    # setup console handler
    handlers = [_get_console_handler(console_level)]

    # setup file handler
    os.makedirs(log_dir, exist_ok=True)
    dt_utc = datetime.now(pytz.utc).strftime("%Y%m%d-%H%M%S")
    log_file_name = os.path.join(log_dir, f'run-{dt_utc}.log')
    fh = _get_file_handler(log_file_name, file_level)
    handlers.append(fh)

    # add handlers
    logger.handlers = []
    for handler in handlers:
        logger.addHandler(handler)

    # log header and return
    _log_header(logger, dt_utc)
    return logger


def _setup_record_factory():
    """Return custom record factory for formatting logger."""
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        """Set up new record factory."""
        record = old_factory(*args, **kwargs)
        mod_path = record.pathname.split(BASE_DIR)[-1]
        record.module_path = mod_path.replace(os.sep, '.')[1:]
        return record

    logging.setLogRecordFactory(record_factory)


def _get_console_handler(console_level="INFO"):
    """Create console handler with a higher log level."""
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch_format = '%(levelname)s - %(module_path)s - ' \
                'Line: %(lineno)d - %(message)s'
    ch_formatter = logging.Formatter(ch_format)
    ch.setFormatter(ch_formatter)
    return ch


def _get_file_handler(log_filename, file_level="DEBUG"):
    """Create file handler at lower level."""
    fh = logging.FileHandler(log_filename)
    fh.setLevel(file_level)
    fh_formatter = logging.Formatter(
        '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    fh_formatter.converter = time.gmtime
    fh.setFormatter(fh_formatter)
    return fh


def _log_header(logger, dt_utc):
    """Write out log header."""
    logger.info('Logger initialized')
    logger.info(f'Batch Start (UTC): {dt_utc}')

    _log_platform(logger)
    _log_python(logger)
    _log_repo(logger, BASE_DIR)

    # log dependencies
    pkg = [(d.project_name, d.version) for d in pkg_resources.working_set]
    logger.info(f"Installed package versions are: {pkg}")


def _log_platform(logger):
    """Log platform details."""
    logger.info(f"Operating System Name: {os.name}")
    logger.info(f"Platform System Name: {platform.system()}")
    logger.info(f"Platform Version: {platform.release()}")
    logger.info(f"Sysconfig: {sysconfig.get_platform()}")
    logger.info(f"Machine Name: {platform.machine()}")
    logger.info(f"Machine Architecture: {platform.architecture()}")


def _log_python(logger):
    """Log python details."""
    logger.info(f"Python Version: {sys.version}")


def _log_repo(logger, repo_dir=None):
    """Log git info."""
    _git = git_info(repo_dir)
    logger.info(f"The current git repo is: {_git['repo']}")
    logger.info(f"The current git branch is: {_git['branch']}")
    logger.info(f"The current git commit is: {_git['commit']}")
    logger.info(f"The current git commit user is: {_git['author']}")


def git_info(repo_dir):
    """Return git info dict.

    Args:
        repo_dir (str): path to repo

    Returns:
        dct: git details including current branch, commit hash, commit summary
             and commit author
    """
    try:
        repo = git.Repo(repo_dir)
        commit = repo.head.commit
        author = repo.git.show("-s", "--format=%an <%ae>", commit.hexsha)
        return {'repo': basename(repo_dir),
                'branch': str(repo.active_branch),
                'commit': commit.hexsha,
                'summary': commit.summary,
                'author': author}
    except git.exc.InvalidGitRepositoryError:
        return None
