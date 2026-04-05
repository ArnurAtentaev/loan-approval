from pydantic import BaseModel


class S3StorageConfig(BaseModel):
    root_user: str
    root_password: str
    host: str = "minio3"
    port_service: int
