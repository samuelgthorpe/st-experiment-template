"""
Insert New description. The old pyweave stuff got trashed so I am going with a
way low-tech solution for building these reports that seems pretty robust


# NOTES
# ----------------------------------------------------------------------------|

Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
from os.path import dirname, join
from subprocess import call
from copy import deepcopy
import json
from datetime import datetime


# # Globals
# -----------------------------------------------------|
REPORT_DIR = join('run', 'report')
REPORT_TEMPLATE = join(dirname(__file__), 'report_template.ipynb')
CELL_TEMPLATE = {'source': [], 'cell_type': 'markdown', 'metadata': {}}


# # Main Report Class for Inheritance
# -----------------------------------------------------|
class Report():
    """Report class."""

    def __init__(self, report_items, **params):
        """Initialize."""
        self.title = params.get('title', self._get_default_title())
        self.tagline = params.get('tagline', self._get_default_tagline())
        self.desc = params.get('desc', self._get_default_description())
        self.report = self._build_report(report_items)

    # # Default report methods
    # -----------------------------------------------------|
    def _get_default_title(self):
        """Return default report title."""
        pass

    def _get_default_tagline(self):
        """Return default report tagline."""
        pass

    def _get_default_description(self):
        """Return default report description."""
        pass

    def _get_default_filename(self):
        """Return default report file name."""
        pass

    # # Main report generation methods
    # -----------------------------------------------------|
    def _build_report(self, report_items):
        """Compile report: update template & add items."""
        report = self._update_template()
        for item in report_items:
            self._add_item_cells(report, item)

        return report

    def _update(self):
        """Update report title, tagline, description & date."""
        report = json.load(open(REPORT_TEMPLATE, 'rb'))
        src = report['cells'][0]['source']
        src[2] = f'<h1>{self.title}</h1>\n'
        src[3] = f'<i>{self.tagline}</i>\n'
        src[7] = self.desc
        src[11] = f'Written {datetime.now().strftime("%B %d, %Y")}\n'

        return report

    @staticmethod
    def _add_item_cells(report, item):
        """Add new cells for the report item."""
        report['cells'].append(deepcopy(CELL_TEMPLATE))
        src = ['\n<h1>{}</h1>'.format(item['hdr']), '\n\n', '---', '\n']
        for arr in src:
            report['cells'][-1]['source'].append(arr)
        report['cells'].append(deepcopy(CELL_TEMPLATE))
        tmp = report['cells'][-1]['source']
        tmp.append('<i>Item Description:</i>\n')
        tmp.append('{}\n'.format(item['desc']))
        tmp.append('{}\n'.format(item['content']))

    def export(self, report_fn=None):
        """Write out the report and convert to html."""
        if report_fn is None:
            report_fn = self._get_default_filename()
        report_dir = join(REPORT_DIR, report_fn)
        os.makedirs(report_dir, exist_ok=True)

        report_pth = join(report_dir, f'{report_fn}.ipynb')
        with open(report_pth, "w") as fh:
            json.dump(self.report, fh, indent=4)
        call(['jupyter', 'nbconvert', '--to', 'html', report_pth])


# # Genral Report Building Helpers
# -----------------------------------------------------|
def report_item(hdr=None, desc=None, content=None):
    """Return report item default cell."""
    return dict(hdr=hdr, desc=desc, content=content)


def report_img(pth, hdr='Figure', desc='insert description'):
    """Structure saved image as report item."""
    item = report_item(hdr, desc)
    item['content'] = '<div><img hr align=left src={}></div>'.format(pth)
    return item


def report_table(dfr, hdr='Table', desc='insert description'):
    """Structure dataframe table as report item."""
    item = report_item(hdr, desc)
    item['content'] = dfr.to_html(index=True, float_format='{:.2f}'.format)
    return item
