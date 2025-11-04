"""
Module housing class to run basic blocked DS experiment.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from logging import getLogger
import os
from os.path import join
import importlib
import hashlib
from functools import partial, lru_cache
from datetime import datetime
import dill
import numpy as np
from sampy.utils import load_yaml
from sampy.utils.logger import log_exceptions
from sampy.utils.aws_s3 import AwsS3
from st_experiment_template import BASE_DIR
from st_experiment_template.experiment.report import Report


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
        self.blocks = {}
        self.data = {}
        self.report_items = []

    def _build(self):
        """Build experiment from cfg."""
        for block_idx, (cls_name, block_params) in enumerate(self.cfg.items()):
            block_src = importlib.import_module(block_params['module'])
            block_obj = getattr(block_src, cls_name)
            block_obj._data = self.data
            block_obj._report_items = self.report_items
            block_obj._out_dir = f'{self.out_dir}/{block_idx}-{cls_name}'

            # set rng seed if specified
            if self.params.get('block_rng_seed') is True:
                if 'rng_seed' not in block_params:
                    block_params['rng_seed'] = self._get_deterministic_seed(
                        block_params, cls_name)

            yield (block_obj, block_params)

    def _get_deterministic_seed(self, block_params, cls_name, base_seed=8888):
        """Return the deterministic rng seed to initialize in block."""
        seed_str = f'{cls_name}-{block_params["module"]}-{base_seed}'
        digest = hashlib.sha256(seed_str.encode()).digest()

        return int.from_bytes(digest[:4], 'little')

    # # Run Entry
    # -----------------------------------------------------|
    @log_exceptions()
    def run(self):
        """Run the experiment & report/push if specified"""
        logger.info('running experiment')
        for block_idx, (block_obj, params) in enumerate(self.src):
            self.blocks[block_idx] = block_obj(**params)
            self.blocks[block_idx].run()

        # check configurable experiment params
        for param in ['report', 'push']:
            params = self.params.get(param)
            if params:
                params = {} if params is True else params
                getattr(self, f'_{param}')(params)

    # # Configurable experiment param helpers
    # -----------------------------------------------------|
    def _report(self, report_params):
        """Create experiment report."""
        logger.info('creating report')
        report = Report(self.report_items, **report_params)
        report.export()

    def _push(self, push_params):
        """Push experiment outputs as configured."""
        logger.info('pushing experiment')
        _now_ = datetime.now().strftime('%Y%m%d-%H%M%S')
        cfg_prefix = push_params.get('prefix', '')
        prefix = join(cfg_prefix, BASE_DIR, f'run-{_now_}')

        s3 = AwsS3()
        s3.upload_folder_to_s3(
            local_dir='run',
            bucket_name=push_params['bucket'],
            prefix=prefix
        )


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
        self.params = params

        # make out_dir and attach params
        os.makedirs(self._out_dir, exist_ok=True)
        for key, val in params.items():
            setattr(self, f'_{key}', val)

        # set rng seed if specified
        if hasattr(self, '_rng_seed'):
            np.random.seed(self._rng_seed)

    def run(self):
        """Overwrite run method."""
        pass

    def fail(self, msg):
        """Raise custom class exception on failure."""
        raise self.exc(msg)

    def _cache(self, dat, file_name, prefix=None):
        """Save pickled binary file."""
        logger.info(f'saving {file_name}')
        if prefix is not None:
            file_name = join(prefix, file_name)
        with open(join(self._out_dir, file_name), 'wb') as pkl:
            dill.dump(dat, pkl)

    @lru_cache
    def _load(self, file_name, prefix=None):
        """Load pickled binary file."""
        logger.info(f'loading {file_name}')
        if prefix is not None:
            file_name = join(prefix, file_name)
        with open(join(self._out_dir, file_name), 'rb') as pkl:
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

    outputs = {}

    def __init__(self, **params):
        """Instantiate class.

        Args:
            **params: Dict of params set in config
        """
        super().__init__(**params)
        self.run = self._wrap_check_run(self.run)

    def _wrap_check_run(self, run_method):
        """Return wrapped run method with check/load functionality.

        Note: This method looks for specified outputs in self.outputs and
              checks if they are present in the output directory. If all
              outputs are present and self._recompute is not True, the outputs
              are loaded from disk. Otherwise, the original run method is
              executed and the outputs are cached to disk.
        """
        def inner():
            logger.info(f'running {self.__class__.__name__}')
            if self._recompute is True or not self._outputs_present():
                run_outputs = run_method()
                for key, file in self.outputs.items():
                    out_pth = f'{self._out_dir}/{file}'
                    self._cache(run_outputs[key], out_pth)
                    self._data[key] = partial(self._load, out_pth)
            else:
                for key, file in self.outputs.items():
                    out_pth = f'{self._out_dir}/{file}'
                    self._data[key] = partial(self._load, out_pth)

        return inner

    def _outputs_present(self):
        """Return False if any outputs are missing."""
        for key, file in self.outputs.items():
            out_pth = f'{self._out_dir}/{file}'
            if not os.path.exists(out_pth):
                return False

        return True

    def _run(self):
        """Overwrite this run method."""
        pass
