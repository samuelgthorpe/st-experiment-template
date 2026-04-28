"""
Module housing tools for publishing experiment.

# NOTES
# ----------------------------------------------------------------------------|


Written April 28, 2026
By Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
from logging import getLogger
from os.path import join
from datetime import datetime
from st_experiment_template import BASE_DIR
from st_experiment_template.utils.aws_s3 import AwsS3
logger = getLogger(__name__)


# # Primary Class
# -----------------------------------------------------|
class Publisher:
    """Class to publish experiment artifacts to S3 and register in MLFlow."""

    cfg_exc = type('PublishCfgException', (Exception,), {})

    def __init__(self, params):
        """Initialize."""
        logger.info('initializing publisher')
        self.params = params

    def publish(self):
        """Publish experiment outputs as configured."""
        logger.info('publishing experiment')
        _now_ = datetime.now().strftime('%Y%m%d-%H%M%S')
        prefix = '/'.join([self.params['prefix'], f'run-{_now_}'])

        # push experiment artifacts to S3
        s3 = AwsS3()
        s3.push_folder_to_s3(
            local_dir=join(BASE_DIR, 'run'),
            bucket_name=self.params['bucket'],
            prefix=prefix
        )

    @classmethod
    def validate_publish_params(cls, params):
        """Validate and normalize publish configuration."""
        if not isinstance(params, dict):
            raise cls.cfg_exc("ExperimentParams.publish must be a mapping.")

        bucket = params.get('bucket')
        if not isinstance(bucket, str) or not bucket.strip():
            raise cls.cfg_exc("ExperimentParams.publish.bucket must be "
                              "a non-empty string.")

        prefix = params.get('prefix')
        if not isinstance(prefix, str) or not prefix.strip():
            raise cls.cfg_exc("ExperimentParams.publish.prefix must be "
                              "a non-empty string.")