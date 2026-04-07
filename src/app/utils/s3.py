import io
from botocore.exceptions import ClientError, BotoCoreError
from boto3.exceptions import S3UploadFailedError
import joblib
import logging

logging.basicConfig(level=logging.INFO)


class S3Storage:
    def __init__(self, client, bucket):
        self.client = client
        self.bucket = bucket

    def load_from_s3(self, key):
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            buffer = io.BytesIO(response["Body"].read())
            buffer.seek(0)

            obj = joblib.load(buffer)
            return obj
        except ClientError as e:
            error = e.response["Error"]["Code"]
            if error == "NoSuchBucket":
                raise RuntimeError(
                    f"Bucket {self.bucket} does not exist. Check config."
                ) from e
            elif error == "NoSuchKey":
                raise RuntimeError(f"Object with key '{key}' not found in bucket.")
            else:
                raise

    def save_object(self, key, obj):
        try:
            buffer = io.BytesIO()
            joblib.dump(obj, buffer)
            buffer.seek(0)

            self.client.put_object(Bucket=self.bucket, Key=key, Body=buffer)
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucket":
                raise RuntimeError(f"Bucket {self.bucket} does not exist. Check config")
