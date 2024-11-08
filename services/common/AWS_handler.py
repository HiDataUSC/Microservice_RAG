from services.indexing.env import AWS_S3_BUCKET, AWS_RDS
from services.common.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, USER_NAME

import os
import boto3
import pymysql
from botocore.exceptions import NoCredentialsError, ClientError
import logging


class S3Handler:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

    def upload_file(self, file_name, folder_prefix=None, object_name=None, metadata=None):
        """Upload a file to an S3 bucket."""
        if object_name is None:
            object_name = file_name

        if folder_prefix is None:
            user_folder = f"{USER_NAME}/"
        else:
            user_folder = f"{USER_NAME}/{folder_prefix}/"
        try:
            response = self.s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix=user_folder)
            if 'Contents' not in response:
                self.s3.put_object(Bucket=AWS_S3_BUCKET, Key=user_folder)

            if metadata:
                if isinstance(metadata, dict):
                    metadata_dict = {f"{key}": str(value) for key, value in metadata.items()}
                else:
                    raise ValueError("Metadata should be a dictionary with key-value pairs.")
                extra_args = {'Metadata': metadata_dict}
            else:
                extra_args = None

            response = self.s3.upload_file(file_name, AWS_S3_BUCKET, f"{user_folder}{object_name}", ExtraArgs=extra_args)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def download_file(self, folder_prefix, dst_folder, object_name_prefix=None):
        """Download files from an S3 bucket.
        
        :param folder_prefix: S3 folder prefix
        :param object_name_prefix: S3 object name prefix (optional)
        :param dst_folder: Local folder path to save the downloaded files
        :return: True if files were downloaded, else False
        """
        try:
            full_prefix = f"{USER_NAME}/{folder_prefix}/"
            if object_name_prefix:
                full_prefix += object_name_prefix

            response = self.s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix=full_prefix)
            if 'Contents' not in response:
                print(f"No files found with prefix {full_prefix} in bucket {AWS_S3_BUCKET}")
                return False
            
            for obj in response['Contents']:
                object_key = obj['Key']
                if object_key.endswith('/') and obj['Size'] == 0:
                    continue

                file_name = os.path.join(dst_folder, os.path.basename(object_key))
                self.s3.download_file(AWS_S3_BUCKET, object_key, file_name)
            
            return True
        
        except NoCredentialsError:
            print("Credentials not available")
            return False
        except ClientError as e:
            logging.error(e)
            return False

class RDBHandler:
    def __init__(self):
        self.connection = self.connect_to_rds()

    def connect_to_rds(self):
        return pymysql.connect(
            host=AWS_RDS['host'],
            user=AWS_RDS['user'],
            password=AWS_RDS['password'],
            db=AWS_RDS['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    def upload_data(self, table_name, data):
        with self.connection.cursor() as cursor:
            for record in data:
                placeholders = ', '.join(['%s'] * len(record))
                columns = ', '.join(record.keys())
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(record.values()))
        self.connection.commit()

    def download_data(self, table_name):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM {table_name}"
            cursor.execute(sql)
            result = cursor.fetchall()
        return result

    def close_connection(self):
        self.connection.close()