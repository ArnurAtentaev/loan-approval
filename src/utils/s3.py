import io
import boto3
import joblib
import logging
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO)


def s3_connector(
    client_name: str, port: int, access_key_id: int, secret_access_key: int
):
    try:
        conn = boto3.client(
            client_name,
            endpoint_url=f"http://localhost:{port}",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
        return conn
    except Exception as e:
        logging.error(f"{e}: Could not connect to s3 storage")


def load_from_s3(client, bucket: str, key):
    response = client.get_object(Bucket=bucket, Key=key)
    buffer = io.BytesIO(response["Body"].read())
    buffer.seek(0)

    obj = joblib.load(buffer)
    return obj


def upload_to_s3(s3_client, bucket_name: str, file_obj, key: str):
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name)

    s3_client.put_object(Bucket=bucket_name, Key=key, Body=file_obj)


def save_object(s3_client, obj, bucket, key):
    buffer = io.BytesIO()
    joblib.dump(obj, buffer)
    buffer.seek(0)

    upload_to_s3(s3_client, bucket, buffer, key)
