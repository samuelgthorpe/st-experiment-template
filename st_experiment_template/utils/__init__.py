"""
Module housing common utils methods.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from os import listdir, getpid
from os.path import join, splitext
import logging
import traceback
import json
import time
import psutil
import yaml


# # Custom Exception Classes
# -----------------------------------------------------|
FilterFilesException = type('FilterFilesException', (Exception,), {})


# # Common Helpers
# -----------------------------------------------------|
def load_yaml(pth):
    """Load specified yaml file.

    Args:
        pth (str): path to yaml config file

    Returns:
        (dct): yaml cfg as dict
    """
    with open(pth, 'r') as file:
        return yaml.safe_load(file)


# # Defs
# -----------------------------------------------------|
def filter_files(data_dir, ext=None, tag=None, **kwrgs):
    """Return files in specified directory which contain tag/ext.

    Args:
        data_dir (str): path to data directory
        ext (str, optional): return only files with this extention
        tag (str, optional): return only files with names including this tag
        **kwrgs: Description

    Returns:
        list: returned string file names

    Raises:
        FilterFilesException: Description
    """
    files = listdir(data_dir)

    # check if extension filter is provided/valid
    if isinstance(ext, str):
        files = [x for x in files if splitext(x)[-1] == ext]
    elif ext is not None:
        raise FilterFilesException(f'invalid file extension specifier: {ext}')

    # check if filter tag is provided/valid
    if isinstance(tag, str):
        files = [x for x in files if tag in x]
    elif tag is not None:
        raise FilterFilesException(f'invalid filename pattern tag: {tag}')

    # if file list has one element return it, o.w. return full list
    files = [join(data_dir, x) for x in files]
    if len(files) == 0:
        if kwrgs.get('none_if_empty', False):
            return None
    if len(files) == 1:
        return files[0]
    return files


# # Timing Decorator
# -----------------------------------------------------|
def timer(method):
    """Wrap the input function call with timing info.

    Args:
        method (method): method to be wrapped in timer

    Returns:
        method: wrapped method with timing logged
    """
    logger = logging.getLogger(__name__)

    def _wrap_method(*args, **kwrgs):
        """Wrap method in check-load-do logic."""
        start = time.time()
        logger.info(f'running {method.__name__} ... ')
        out = method(*args, **kwrgs)
        msg = '{} complete in {:.2f} sec'.\
            format(method.__name__, time.time() - start)
        logger.info(msg)
        return out
    return _wrap_method


# # Try-Catch-Log Decorator
# -----------------------------------------------------|
def try_catch_log(*dec_args, **dec_kwrgs):
    """Wrap a method in a try, catch, log statement.

    Args:
        *dec_args:
        **dec_kwrgs:

    Returns:
        method: method with try-catch-log details
    """

    def _try_catch_log_decorator(method):
        """Decorate the wrapped method with try_catch_log params."""
        logger = logging.getLogger(__name__)
        verbose = dec_kwrgs.get('verbose', False)

        def wrap_method(*args, **kwrgs):
            """Wrap method in try-catch with standardized logging."""
            meth_str = method.__str__().split()[1]
            if verbose:
                logger.info(f'Running: {meth_str}')

            try:
                outputs = method(*args, **kwrgs)
                if verbose:
                    logger.info(f'Success: {meth_str}')
                return outputs
            except Exception as err:  # pylint: disable=broad-except

                if len(dec_args):
                    exc_type = dec_args[0]
                    logger.error(_get_exception_str(err, raise_as=exc_type))
                    raise exc_type(err)
                else:
                    logger.error(_get_exception_str(err))
                    raise err

        return wrap_method
    return _try_catch_log_decorator


def _get_exception_str(err, raise_as=None):
    """Simplify and clean logs for exceptions.

    Args:
        err (Exception instance): caught exception
        raise_as (Exception Class, optional): custom Exception ctype to raise

    Returns:
        TYPE: Description
    """
    exc_type = raise_as if raise_as else err.__class__
    return json.dumps({"errorType": exc_type.__name__,
                       "errorMessage": str(err),
                       "stackTrace": traceback.format_exception(err)})


# # Memory Profile Decorator
# -----------------------------------------------------|
def memory_profile(func):
    """Wrap a method with memory profileing decorator.

    Args:
        func (method): function to profile

    Returns:
        (method): wrapped method
    """
    def wrapper(*args, **kwargs):

        mem_before = _process_memory()
        result = func(*args, **kwargs)
        mem_after = _process_memory()
        logger.info("{}:consumed memory: {:,}".format( # noqa
            func.__name__,
            mem_before, mem_after, mem_after - mem_before))

        return result
    return wrapper


def _process_memory():
    """Inner psutil function for memory profiler."""
    process = psutil.Process(getpid())
    mem_info = process.memory_info()
    return mem_info.rss
