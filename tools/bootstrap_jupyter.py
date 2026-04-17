"""
Insert description.

# NOTES
# ----------------------------------------------------------------------------|


Written April 17, 2026
By Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from __future__ import annotations
import subprocess
import sys


# # Globals
# -----------------------------------------------------|
KERNEL_NAME = "st-experiment-template"
DISPLAY_NAME = "Python (st-experiment-template)"


# # Defs
# -----------------------------------------------------|
def main():
    """Run main method."""
    print(f"Using Python: {sys.executable}")
    print(f"Using prefix: {sys.prefix}")
    print()

    run([
        sys.executable,
        "-m",
        "ipykernel",
        "install",
        "--prefix",
        sys.prefix,
        "--name",
        KERNEL_NAME,
        "--display-name",
        DISPLAY_NAME,
    ])

    print()
    print("Kernel installed successfully.")
    print(f"Kernel name: {KERNEL_NAME}")
    print(f"Display name: {DISPLAY_NAME}")
    print()
    print("You can verify with:")
    print("  jupyter kernelspec list")


def run(cmd: list[str]) -> None:
    """Run command and print it."""
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


# # Main Entry
# -----------------------------------------------------|
if __name__ == "__main__":
    main()
