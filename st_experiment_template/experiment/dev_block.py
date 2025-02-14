"""
Module housing experiment block template for dev.

# NOTES
# ----------------------------------------------------------------------------|

Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from logging import getLogger
from st_experiment_template.experiment import Block
logger = getLogger(__name__)


# # Experiment Block Example Class 1
# -----------------------------------------------------|
class DevBlock(Block):
    """Experiment block class."""

    def __init__(self, **params):
        """Instantiate class.

        Args:
            **params: Dict of params set in config
        """
        super().__init__(**params)

    def run(self):
        """Run main method."""
        logger.info(f'running {self.__class__.__name__}')

        from sampy.common import keyboard
        keyboard(locals(), globals())
