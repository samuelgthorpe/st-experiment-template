"""
Module housing class to run basic blocked DS experiment.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
import importlib
from logging import getLogger
from functools import partial
import dill
from sampy.utils import load_yaml
from sampy.utils.logger import log_exceptions
from st_experiment_template import BASE_DIR


# # Globals
# -----------------------------------------------------|
logger = getLogger(__name__)
log_exceptions = partial(log_exceptions, logger=logger)


# # Primary Class
# -----------------------------------------------------|
class Experiment:
    """Class to run basic blocked DS experiment."""

    out_dir = os.path.join(BASE_DIR, 'run', 'batch')

    @log_exceptions()
    def __init__(self, cfg_file: str, **kwrgs):
        """Initialize class.

        Args:
            cfg_file (str): path to experiment config .yaml
            **kwrgs
        """
        logger.info('initializing experiment')
        self.exc = type(f'{self.__class__.__name__}Error', (Exception,), {})
        self.cfg = load_yaml(cfg_file)
        self.params = self.cfg.pop('ExperimentParams', {})
        self.src = self._build()
        self.data = {}
        self.blocks = {}

    def _build(self):
        """Build experiment from cfg."""
        for block_idx, (cls_name, block_params) in enumerate(self.cfg.items()):
            block_src = importlib.import_module(block_params['module'])
            block_obj = getattr(block_src, cls_name)
            block_obj._exp_data = self.data
            block_obj._out_dir = f'{self.out_dir}/{block_idx}-{cls_name}'
            yield (block_obj, block_params)

    # # Run Entry
    # -----------------------------------------------------|
    @log_exceptions()
    def run(self):
        """Run the experiment."""
        logger.info('running experiment')

        # run experiment
        for block_idx, (block_obj, params) in enumerate(self.src):
            self.blocks[block_idx] = block_obj(**params)
            self.blocks[block_idx].run()

        # check report
        if self.params.get('report', False):
            self._report()

        # check push
        if self.params.get('push', False):
            self._push()

    def fail(self, msg):
        """Raise custom class exception on failure."""
        raise self.exc(msg)

    # # Report & Push Helpers
    # -----------------------------------------------------|
    def _report(self):
        """Create experiment report."""
        logger.info('creating report: Not yet implemented')

    def _push(self, msg):
        """Push experiment outputs as configured."""
        logger.info('pushing experiment: Not yet implemented')


# # Experiment Block Base Class
# -----------------------------------------------------|
class Block:
    """Initialize class."""

    def __init__(self, **params):
        """Instantiate class.

        Args:
            **params: Dict of params set in config
        """
        logger.info(f'initializing {self.__class__.__name__}')
        self.exc = type(f'{self.__class__.__name__}Error', (Exception,), {})

        # make out_dir and attach params
        os.makedirs(self._out_dir, exist_ok=True)
        for key, val in params.items():
            setattr(self, f'_{key}', val)

    def run(self):
        """Overwrite run method."""
        pass

    def fail(self, msg):
        """Raise custom class exception on failure."""
        raise self.exc(msg)

    @staticmethod
    def _cache(dat, file_name):
        """Save pickled binary file."""
        logger.info(f'saving {file_name}')
        with open(file_name, 'wb') as pkl:
            dill.dump(dat, pkl)

    @staticmethod
    def _load(file_name):
        """Load pickled binary file."""
        logger.info(f'loading {file_name}')
        with open(file_name, 'rb') as pkl:
            return dill.load(pkl)

    @staticmethod
    def _import(full_class_name):
        """Import class from pip installed Python libraries."""
        logger.info(f'importing {full_class_name}')
        module_name, class_name = full_class_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        return getattr(module, class_name)


# # CheckRunBlock Base Class
# -----------------------------------------------------|
class CheckRunBlock(Block):
    """Initialize class."""

    out_fn = None

    def run(self):
        """Run main method."""
        out_pth = f'{self._out_dir}/{self.out_fn}.pkl'
        if os.path.exists(out_pth) and self._recompile is False:
            self._exp_data[self.out_fn] = self._load(out_pth)
        else:
            logger.info(f'generating {self.out_fn}')
            self._exp_data[self.out_fn] = self._run()
            self._cache(self._exp_data[self.out_fn], out_pth)

    def _run(self):
        """Overwrite this run method."""
        pass