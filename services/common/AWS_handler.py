from services.indexing.env import AWS_S3_BUCKET
from services.common.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging


class S3Handler:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def upload_file(self, file_name, object_name=None):
        """Upload a file to an S3 bucket."""
        if object_name is None:
            object_name = file_name

        try:
            response = self.s3.upload_file(file_name, AWS_S3_BUCKET, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def download_file(self, object_name_prefix, dst_folder, bucket=None):
        """Download a file from an S3 bucket.
        
        :param object_name_prefix: S3 object name prefix
        :param file_name: Local file path to save the downloaded file
        :param bucket: Bucket to download from (default is from environment variable)
        :return: True if file was downloaded, else False
        """
        if bucket is None:
            bucket = AWS_S3_BUCKET

        try:
            response = self.s3.list_objects_v2(Bucket=bucket, Prefix=object_name_prefix)
            if 'Contents' not in response:
                print(f"No files found with prefix {object_name_prefix} in bucket {bucket}")
                return False
            
            object_key = response['Contents'][0]['Key']
            print(f"Found object: {object_key}")

            file_name = os.path.join(dst_folder, os.path.basename(object_key))
            print(f"Downloading {object_key} from bucket {bucket}")
            self.s3.download_file(bucket, object_key, file_name)
            print(f"Download successful: {file_name}")
            return True
        
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except ClientError as e:
            logging.error(e)
            return False
