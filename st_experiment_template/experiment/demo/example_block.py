"""
Module housing example experiment block classes.

# NOTES
# ----------------------------------------------------------------------------|
Example data/visualization taken from:
https://matplotlib.org/stable/gallery/mplot3d/
stem3d_demo.html#sphx-glr-gallery-mplot3d-stem3d-demo-py


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from logging import getLogger
import numpy as np
from st_experiment_template.experiment import Block, CheckRunBlock
logger = getLogger(__name__)


# # Experiment Block Example Class 1
# -----------------------------------------------------|
class ExampleBlock1(Block):
    """Example experiment block class."""

    def run(self):
        """Run main method.

        NOTE: _exp_data allows data to persist in-memory across blocks.
              For large blocks that take a long time to execute it may be
              more convenient in development to cache intermediate outputs
              to disk and load as needed in subsequent blocks.
        """
        logger.info(f'running {self.__class__.__name__}')
        self._data['theta'] = np.linspace(0, 2*np.pi)


# # Experiment Block Example Class 2
# -----------------------------------------------------|
class ExampleBlock2(CheckRunBlock):
    """Example experiment block class demonstrating the CheckRunBlock."""

    outputs = dict(x='x.pkl', y='y.pkl', z='z.pkl')

    def run(self):
        """Run main method."""
        logger.info(f'running {self.__class__.__name__}')
        self._data['x'] = np.cos(self._data['theta'] - np.pi/2)
        self._data['y'] = np.sin(self._data['theta'] - np.pi/2)
        self._data['z'] = self._data['theta']

        return dict(x=self._data['x'], y=self._data['y'], z=self._data['z'])
