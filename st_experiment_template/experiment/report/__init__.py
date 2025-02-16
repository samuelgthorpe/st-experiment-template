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
from os.path import basename, dirname, join
import json
from datetime import datetime
from subprocess import call
from st_experiment_template import BASE_DIR


# # Globals
# -----------------------------------------------------|
REPORT_DIR = join('run', 'report')
REPORT_TEMPLATE = join(dirname(__file__), 'report_template.ipynb')


# # Main Report Class for Inheritance
# -----------------------------------------------------|
class Report():
    """Report class."""

    def __init__(self, report_items, **params):
        """Initialize."""
        self.title = params.get('title', basename(BASE_DIR))
        self.tagline = params.get('tagline', '')
        self.desc = params.get('description', 'insert experiment description.')
        self.report_fn = params.get('report_fn')
        self.report = self._build_report(report_items)

    def _build_report(self, report_items):
        """Compile report: update template & add items."""
        report = self._update_template()
        for item in report_items:
            self._add_item(report, item)

        return report

    def _update_template(self):
        """Update report title, tagline, description & date."""
        report = json.load(open(REPORT_TEMPLATE, 'rb'))
        src = report['cells'][0]['source']
        src[2] = f'<h1>{self.title}</h1>\n'
        src[3] = f'<i>{self.tagline}</i>\n'
        src[7] = f'{self.desc}\n'
        src[11] = f'Written {datetime.now().strftime("%B %d, %Y")}\n'

        return report

    @staticmethod
    def _add_item(report, item):
        """Add new cells for the report item."""
        report['cells'].append(report_cell(
            source=[f'<h2>{item["hdr"]}</h2>', '\n\n', '---', '\n']
        ))
        report['cells'].append(report_cell(
            cell_type=item['type'],
            source=[
                f'\n<i>Item Description:</i> {item['desc']}\n',
                f'{item['content']}\n'
            ]
        ))

    def export(self):
        """Write out the report and convert to html."""
        if self.report_fn is None:
            now = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.report_fn = f'{basename(BASE_DIR)}-{now}'

        report_dir = join(REPORT_DIR, self.report_fn)
        os.makedirs(report_dir, exist_ok=True)

        report_pth = join(report_dir, f'{self.report_fn}.ipynb')
        with open(report_pth, "w") as fh:
            json.dump(self.report, fh, indent=4)
        call(['jupyter', 'nbconvert', '--to', 'html', report_pth])


# # Report building helpers
# -----------------------------------------------------|
def report_cell(source=[], metadata={}, cell_type='markdown'):
    """Return report cell with specified fields."""
    return dict(source=source, cell_type=cell_type, metadata=metadata)


def report_item(hdr=None, desc=None, content=None, type='markdown'):
    """Return report item default cell."""
    return dict(hdr=hdr, desc=desc, content=content, type=type)


def report_img(pth, hdr='Figure', desc='insert description'):
    """Structure saved image as report item."""
    return report_item(hdr, desc, f'<div><img hr align=left src={pth}></div>')


def report_table(dfr, hdr='Table', desc='insert description'):
    """Structure dataframe table as report item."""
    table_html = dfr.to_html(index=True, float_format='{:.2f}'.format)
    return report_item(hdr, desc, content=table_html)


def report_html(content, hdr='Figure', desc='insert description'):
    """Structure html figure as report item."""
    return report_item(hdr, desc, content, type='raw')
