import logging

from pydantic import BaseModel
from prometheus_client import start_http_server

logging.basicConfig(level=logging.INFO)


class PrometheusConfig(BaseModel):
    port_service: int
