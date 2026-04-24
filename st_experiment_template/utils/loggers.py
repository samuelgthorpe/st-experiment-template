"""
Module to house logging tools.

# NOTES
# ----------------------------------------------------------------------------|


written March 2024
by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import sys
import os
import platform
import sysconfig
from os.path import basename
import shutil
import logging
import git
from importlib.metadata import distributions
from datetime import datetime, timezone
import time
import functools
import json
import pandas as pd


# # Primary init log method
# -----------------------------------------------------|
def init_log(base_dir, console_level="INFO", file_level="INFO", **kwrgs):
    """Initialize logger.

    Args:
        console_level (str, optional): console logging level, e.g. WARNING
        file_level (str, optional): file logging level, e.g. DEBUG
        **kwrgs: Description

    Returns:
        root logger
    """
    run_dir = os.path.join(base_dir, 'run')
    log_dir = os.path.join(run_dir, 'logs')
    logger = logging.getLogger("root")
    logger.setLevel(logging.DEBUG)
    _setup_record_factory(base_dir)

    # setup console handler
    handlers = [_get_console_handler(console_level)]

    # setup file handler
    os.makedirs(log_dir, exist_ok=True)
    runtime_utc = kwrgs.get('runtime_utc')
    if runtime_utc is None:
        runtime_utc = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    log_file_name = os.path.join(log_dir, f'run-{runtime_utc}.log')
    fh = _get_file_handler(log_file_name, file_level)
    handlers.append(fh)

    # add handlers
    logger.handlers = []
    for handler in handlers:
        logger.addHandler(handler)

    # log header and return
    _log_header(logger, base_dir, runtime_utc)
    return logger


def _setup_record_factory(base_dir):
    """Return custom record factory for formatting logger."""
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        """Set up new record factory."""
        record = old_factory(*args, **kwargs)
        mod_path = record.pathname.split(base_dir)[-1]
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
    # fh_formatter = logging.Formatter(
    #     '%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    fh_formatter = JsonFormatter()
    fh_formatter.converter = time.gmtime
    fh.setFormatter(fh_formatter)
    return fh


def _log_header(logger, base_dir, dt_utc):
    """Write out log header."""
    logger.info('Logger initialized')
    logger.info(f'Batch Start (UTC): {dt_utc}')

    _log_platform(logger)
    _log_python(logger)
    _log_repo(logger, base_dir)

    # log dependencies
    pkg = [(dist.metadata["Name"], dist.version) for dist in distributions()]
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
    try:
        _git = git_info(repo_dir)
        logger.info(f"The current git repo is: {_git['repo']}")
        logger.info(f"The current git branch is: {_git['branch']}")
        logger.info(f"The current git commit is: {_git['commit']}")
        logger.info(f"The current git commit user is: {_git['author']}")
    except Exception as err:
        logger.warning(f'Error logging .git repo: {err}')


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


# # Log Exception Decoratpr
# -----------------------------------------------------|
def log_exceptions(logger=None, raise_exception=True):
    """Return decorator to wrap method in try catch to log exceptions, etc."""
    logger = logger or logging.getLogger()

    def decorator(func):
        @functools.wraps(func)  # Preserve function metadata
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{func.__name__}: {e}", exc_info=True)
                if raise_exception:
                    raise e from None
        return wrapper
    return decorator


# # Json Log Formatter
# -----------------------------------------------------|
class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON."""

    def format(self, record):
        log_message = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module_path,
            "funcName": record.funcName,
            "lineNo": record.lineno
        }
        # Include exception details if any
        if record.exc_info:
            log_message["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_message)


# # Save copy of cfg file to logs
# -----------------------------------------------------|
def log_cfg(cfg_file, runtime_utc=None):
    """Cache copy of cfg file to log dir."""
    log_dir = os.path.join('run', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    if runtime_utc is None:
        runtime_utc = datetime.now().strftime("%Y%m%d-%H%M%S")
    cfg_log_file = os.path.join(log_dir, f'cfg-{runtime_utc}.yaml')
    shutil.copy(cfg_file, cfg_log_file)