import logging

import boto3
from botocore.client import Config
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)


class LoanConfig(BaseModel):
    host: str = "loan_app"
    port_service: int
