"""
Main entry to run primary st_experiment_template experiment.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from st_experiment_template.utils.logger import init_log
from st_experiment_template.experiment import Experiment


# # Main Method
# -----------------------------------------------------|
def main(cfg_file, **kwrgs):
    """Run main method."""
    init_log()
    exp = Experiment(cfg_file, **kwrgs)
    exp.run()

    return exp


# # Main Entry
# -----------------------------------------------------|
if __name__ == "__main__":  # pragma: no cover
    exp = main("st_experiment_template/cfg.yaml")
