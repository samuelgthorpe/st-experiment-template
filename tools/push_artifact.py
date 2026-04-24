"""
Insert description.

# NOTES
# ----------------------------------------------------------------------------|


Written April 24, 2026
By Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
import shutil
from datetime import datetime
from pathlib import Path


# # Defs
# -----------------------------------------------------|
def main():
    """Run main method."""
    _now_ = datetime.now().strftime('%Y%m%d-%H%M%S')
    run_dir = Path('run')
    artifact = Path('.artifacts') / f'run-{_now_}'
    shutil.copytree(run_dir, artifact, ignore=ignore_batch)


def ignore_batch(dirpath, names) -> set[str]:
    """Ignore large batch output directory."""
    return {"batch"} if "batch" in names else set()


# # Main Entry
# -----------------------------------------------------|
if __name__ == "__main__":
    main()
