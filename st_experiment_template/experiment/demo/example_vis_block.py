"""
Module housing example vis experiment block class.

Note there is absolutely nothing special about a vis block relative to a
processing block, or whatever, this is just a demo. Real experiment
architecture is intended to be whatever it needs to be.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
from logging import getLogger
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio
from st_experiment_template.experiment import Block
from st_experiment_template.experiment.report import report_img_code
from st_experiment_template.experiment.report import report_code_html
logger = getLogger(__name__)


# # Experiment Block Example Class 1
# -----------------------------------------------------|
class ExampleVisBlock(Block):
    """Example experiment visualization block class."""

    desc = '''Example data/visualization taken from:
        https://matplotlib.org/stable/gallery/mplot3d/
        stem3d_demo.html#sphx-glr-gallery-mplot3d-stem3d-demo-py'''

    def run(self):
        """Run main method."""
        if self.params.get('plot_library') != 'plotly':
            self._vis_with_matplotlib()
        else:
            self._vis_with_plotly()

    def _vis_with_matplotlib(self):
        """Return standard matplotlib visualization."""
        fig, axi = plt.subplots(subplot_kw=dict(projection='3d'))
        axi.stem(self._data['x'], self._data['y'], self._data['z'])
        axi.set_title('Example 3D Stem Plot', fontsize=15, fontstyle='italic')

        # save out
        vis_fn = os.path.join(self._out_dir, 'example.png')
        fig.savefig(vis_fn)
        plt.close(fig)
        logger.info(f'saved {vis_fn}')

        # add to report
        self._report_items.append(
            report_img_code(vis_fn, hdr='3D Stem Plot', desc=self.desc)
        )

    def _vis_with_plotly(self):
        """Return plotly visualization."""
        x, y, z = self._data['x'], self._data['y'], self._data['z']
        lines = [
            go.Scatter3d(
                x=[x[i], x[i]],  # Same x value
                y=[y[i], y[i]],  # Same y value
                z=[0, z[i]],     # Line from z=0 to z[i]
                mode="lines",
                line=dict(color="black", width=2),
                showlegend=False
            )
            for i in range(len(x))
        ]

        # Add marker points on top
        points = go.Scatter3d(
            x=x, y=y, z=z,
            mode="markers",
            marker=dict(size=6, color="red"),
            name="Data Points"
        )

        # Combine traces and layout
        fig = go.Figure(data=lines + [points])
        fig.update_layout(
            title="Example 3D Stem Plot",
            scene=dict(
                aspectmode='cube',
                xaxis_title="X Axis",
                yaxis_title="Y Axis",
                zaxis_title="Z Axis"
            )
        )

        # add to report
        vis_fn = os.path.join(self._out_dir, 'example.html')
        pio.write_html(fig, vis_fn, include_plotlyjs='cdn', full_html=False)
        self._report_items.append(
            report_img_code(vis_fn, hdr='3D Stem Plot', desc=self.desc)
        )
