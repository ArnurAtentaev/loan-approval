import logging

from pydantic import BaseModel
from prometheus_client import start_http_server

logging.basicConfig(level=logging.INFO)


class PrometheusConfig(BaseModel):
    port_service: int

    @property
    def connection(self):
        try:
            logging.info(f"TOOK:\n\n{self.port_service}")
            return start_http_server(port=self.port_service)
        except Exception as e:
            logging.error(f"{e}: Could not connect to s3 storage")
