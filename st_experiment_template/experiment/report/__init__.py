"""
Insert New description.

# NOTES
# ----------------------------------------------------------------------------|

Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
from os.path import basename, dirname, join, splitext
import json
from datetime import datetime
from subprocess import call
from st_experiment_template import BASE_DIR


# # Globals
# -----------------------------------------------------|
REPORT_DIR = join('run', 'report')
REPORT_TEMPLATE = join(dirname(__file__), 'report_template.ipynb')
CSS_STYLE_CODE = '''
from IPython.display import HTML, display
display(HTML("""
<style>
img {
    display: block;
    margin-left: auto;
    margin-right: auto;
}
</style>
"""))
'''.strip()


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
        report = self._prepend_style_cell(report)
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

    def _prepend_style_cell(self, report):
        """Prepend the CSS style code block."""
        src = CSS_STYLE_CODE
        meta = {"tags": ["hide_input"]}
        style_cell = report_cell(source=src, metadata=meta, cell_type='code')
        report['cells'].insert(0, style_cell)

        return report

    @staticmethod
    def _add_item(report, item):
        """Add new cells for the report item."""
        report['cells'].append(report_cell(
            source=[
                f'<h2>{item["hdr"]}</h2>', '\n\n', '---', '\n',
                f'\n<i>Item Description:</i> {item["desc"]}\n'
                ]
        ))
        report['cells'].append(report_cell(
            cell_type=item['type'],
            source=[item['content']],
            metadata=item['meta']
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
        cmd = [
            'jupyter',
            'nbconvert',
            '--execute',
            '--TagRemovePreprocessor.enabled=True',
            '--TagRemovePreprocessor.remove_input_tags=["hide_input"]',
            '--HTMLExporter.sanitize_html=False',
            '--no-input',
            '--to',
            'html',
            report_pth
        ]
        call(cmd)


# # Report building helpers
# -----------------------------------------------------|
def report_cell(source=[], metadata={}, outputs=[], cell_type='markdown'):
    """Return report cell with specified fields."""
    cell = dict(source=source, cell_type=cell_type, metadata=metadata)
    if cell_type == 'code':
        cell['outputs'] = outputs
        cell['execution_count'] = 0

    return cell


def report_item(hdr=None, desc=None, content=None, meta={}, type='markdown'):
    """Return report item default cell."""
    return dict(hdr=hdr, desc=desc, content=content, meta=meta, type=type)


def report_img(pth, hdr='Figure', desc='insert description'):
    """Structure saved image as report item."""
    if isinstance(pth, str):
        content = f'<div><img align="left" src="{pth}"></div>'
    elif isinstance(pth, list):
        content = [f'<div><img align="left" src="{x}"></div>' for x in pth]
        content = '\n'.join(content)
    else:
        content = pth

    return report_item(hdr, desc, content)


def report_table(dfr, hdr='Table', desc='insert description'):
    """Structure dataframe table as report item."""
    table_html = dfr.to_html(index=True, float_format='{:.2f}'.format)
    return report_item(hdr, desc, content=table_html)


def report_img_code(pths, hdr='Figure', desc='insert description', **params):
    """Structure html figure as report item."""
    meta = {"tags": ["hide_input"]}
    if isinstance(pths, str):
        pths = [pths]
    elif not isinstance(pths, list):
        raise Exception('must pass img path as string or list of strings!')

    # loop construct content
    for pth in pths:
        if splitext(pth)[-1] == '.html':
            content = ["from IPython.display import IFrame, display"]
            width = params.get('width', '100%')
            height = params.get('height', 600)
            content.append(
                f'display(IFrame("{pth}", width="{width}", height={height}))'
            )
        else:
            content = ["from IPython.display import Image, display"]
            content.append(f'display(Image("{pth}"))')
    content = "\n".join(content)

    return report_item(hdr, desc, content, meta=meta, type='code')


def report_code_html(html_str, hdr='Figure', desc='insert description'):
    """Structure html figure as report item."""
    content = f"""
    from IPython.display import display, HTML
    html_str = '''{html_str}'''

    display(HTML(html_str))
    """
    return report_item(hdr, desc, content, type='code')
