import logging

import boto3
from botocore.client import Config
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)


class S3StorageConfig(BaseModel):
    root_user: str
    root_password: str
    host: str = "minio3"
    port_service: int

    @property
    def connection(self):
        try:
            logging.info(
                f"TOOK:\n\n{self.root_user}\n{self.root_password}\n{self.port_service}"
            )
            return boto3.client(
                "s3",
                endpoint_url=f"http://{self.host}:{self.port_service}",
                aws_access_key_id=self.root_user,
                aws_secret_access_key=self.root_password,
                config=Config(signature_version="s3v4"),
            )
        except Exception as e:
            logging.error(f"{e}: Could not connect to s3 storage")
