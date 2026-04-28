"""
Initialize the optional TeX report scaffold under docs/report.

This tool creates the reusable report directory structure for projects that
need a formal TeX report, then downloads the report template assets from S3.

# NOTES
# ----------------------------------------------------------------------------|


Written April 28, 2026
By Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from pathlib import Path


# # Constants
# -----------------------------------------------------|
DOCS_DIR = Path("docs")
REPORT_DIR = DOCS_DIR / "report"
BUILD_DIR = REPORT_DIR / "build"
S3_BUCKET = "ds-experiment-artifacts"
S3_PREFIX = "templates/tex-report"
S3_FILES = {
    f"{S3_PREFIX}/RPT-00XXX-Report.tex": REPORT_DIR / "RPT-00XXX-Report.tex",
    f"{S3_PREFIX}/Logo.png": REPORT_DIR / "Logo.png",
}


# # Defs
# -----------------------------------------------------|
def _touch_keep_file(path):
    """Create .keep file in the specified directory."""
    keep_file = path / ".keep"
    keep_file.touch(exist_ok=True)


def _check_s3_config():
    """Raise if the S3 template bucket has not been configured."""
    if S3_BUCKET == "INSERT_TEX_REPORT_TEMPLATE_BUCKET":
        raise RuntimeError("Set S3_BUCKET in tools/init_tex_report.py.")
    if S3_PREFIX == "INSERT_TEX_REPORT_TEMPLATE_PREFIX":
        raise RuntimeError("Set S3_PREFIX in tools/init_tex_report.py.")


def _download_report_files():
    """Download report template files from S3."""
    import boto3

    client = boto3.client("s3")
    for s3_key, local_path in S3_FILES.items():
        print(f"Downloading s3://{S3_BUCKET}/{s3_key} -> {local_path}")
        client.download_file(S3_BUCKET, s3_key, str(local_path))


def main():
    """Run main method."""
    if REPORT_DIR.exists():
        print(f"{REPORT_DIR} already exists; nothing to initialize.")
        return

    _check_s3_config()
    print(f"Initializing TeX report directory at {REPORT_DIR}")
    DOCS_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir()
    BUILD_DIR.mkdir()
    _touch_keep_file(REPORT_DIR)
    _touch_keep_file(BUILD_DIR)
    _download_report_files()
    print("TeX report directory initialized.")


# # Main Entry
# -----------------------------------------------------|
if __name__ == "__main__":
    main()
