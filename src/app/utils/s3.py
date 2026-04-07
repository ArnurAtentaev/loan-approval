import io
from boto3.exceptions import Boto3Error, S3UploadFailedError, S3TransferFailedError
import joblib
import logging

logging.basicConfig(level=logging.INFO)


class S3Storage:
    pass


def load_from_s3(client, bucket: str, key):
    try:
        response = client.get_object(Bucket=bucket, Key=key)
        buffer = io.BytesIO(response["Body"].read())
        buffer.seek(0)

        obj = joblib.load(buffer)
        return obj
    except Boto3Error as b3:
        logging.exception(b3)


def upload_to_s3(s3_client, bucket_name: str, file_obj, key: str):
    if not s3_client.head_bucket(Bucket=bucket_name):
        s3_client.create_bucket(Bucket=bucket_name)

    try:
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=file_obj)
    except S3UploadFailedError as u:
        logging.exception(u)


def save_object(s3_client, obj, bucket, key):
    try:
        buffer = io.BytesIO()
        joblib.dump(obj, buffer)
        buffer.seek(0)

        upload_to_s3(s3_client, bucket, buffer, key)
    except S3TransferFailedError as s:
        logging.exception(s)
