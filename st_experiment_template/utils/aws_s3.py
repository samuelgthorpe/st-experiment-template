"""
Module to house AWS S3 client helper class.

# NOTES
# ----------------------------------------------------------------------------|


Written by Samuel Thorpe
"""


# # Imports
# -----------------------------------------------------|
import os
import boto3
from logging import getLogger
from st_experiment_template.utils import try_catch_log


# # Globals
# -----------------------------------------------------|
AwsS3Exception = type('AwsS3Exception', (Exception,), {})
logger = getLogger(__name__)


# # Primary Class
# -----------------------------------------------------|
class AwsS3:
    """AWS S3 client helper class."""

    def __init__(self, session_params=None):
        """Initialize class.

        Args:
            session_params (dct, optional): Dict of optional session params
        """
        self._params = {} if session_params is None else session_params
        self._session = boto3.Session(**self._params)
        self._resource = boto3.resource('s3')

    @try_catch_log(AwsS3Exception)
    def get_file_in_path(self, s3_path, local_dir):
        """Pull specified s3 file to local dir.

        Args:
            s3_path (str): path to file
            local_dir (atr): local directory to save to

        Returns:
            str:local path to file
        """
        logger.info(f"Pulling file {s3_path} to {local_dir}")

        bucket_name, key = s3_path[5:].split('/', 1)
        file_name = s3_path.rsplit('/', 1)[-1]
        output = f"{local_dir}/{file_name}"
        bucket = self._resource.Bucket(bucket_name)
        bucket.download_file(key, output)

        return output

    @try_catch_log(AwsS3Exception)
    def get_files_in_s3_directory(self, s3_dir, local_dir):
        """Pull specified s3 dir to local dir.

        Args:
            s3_dir (str): path to s3 directory to pull
            local_dir (str): local directory to pull to

        Returns:
            list: list of downloaded file info
        """
        logger.info(f"Pulling all files in {s3_dir} to {local_dir}")

        bucket, key = s3_dir[5:].split('/', 1)
        bucket = self._resource.Bucket(bucket)
        outputs = []
        for obj in bucket.objects.filter(Prefix=key):
            file_name = obj.key.split('/')[-1]
            local_path = f"{local_dir}/{file_name}"
            if not obj.key.endswith('/'):
                bucket.download_file(obj.key, local_path)
                outputs.append({
                    "local_path": local_path,
                    "file_name": file_name})

        return outputs

    @try_catch_log(AwsS3Exception)
    def push_files_to_s3(self, local_dir, bucket, s3_dir, **kwrgs):
        """Push specified local dir to s3.

        Args:
            local_dir (str): local directory to push
            bucket (str): bucket to push to
            s3_dir (str): prefix to push to
            **kwrgs: Description
        """
        logger.info(f"Pushing all files in {local_dir} to "
                    f"S3 location: {bucket}/{s3_dir}")

        for file in os.listdir(local_dir):
            if self._check_ignore(file, **kwrgs):
                logger.info(f"ignoring {file}")
                continue

            self.push_file_to_s3(f"{local_dir}/{file}", bucket, s3_dir)

    @staticmethod
    def _check_ignore(file, **kwrgs):
        """Return True if file should be ignored."""
        dss_chk = file == '.DS_Store'
        ext_chk = os.path.splitext(file)[-1] in kwrgs.get('ingore_ext', [])

        return any([dss_chk, ext_chk])

    @try_catch_log(AwsS3Exception)
    def push_file_to_s3(self, local_file, bucket, s3_dir):
        """Push specified local file to s3."""
        logger.info(f"Pushing {local_file} to S3 location: {bucket}/{s3_dir}")

        client = self._session.client('s3')
        local_dir, file = os.path.split(local_file)
        client.upload_file(local_file, bucket, f"{s3_dir}/{file}")
