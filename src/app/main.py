import logging
import pandas as pd
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

import boto3

# rom botocore.client import Config
from prometheus_client import start_http_server

from app.config import settings
from app.utils.s3 import load_from_s3
from app.schemas.model_parameters import UserInfo
from app.metrics.loan_approval import REQUEST_TIME, TOTAL_REQUEST, CLASS_ALLOCATION

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.s3_client = boto3.client(
        "s3",
        endpoint_url=f"http://{settings.s3.host}:{settings.s3.port_service}",
        aws_access_key_id=settings.s3.root_user,
        aws_secret_access_key=settings.s3.root_password,
    )

    app.state.preprocessor = load_from_s3(
        app.state.s3_client,
        bucket="inference-bucket",
        key="preprocessor.pkl",
    )
    app.state.model = load_from_s3(
        app.state.s3_client, bucket="inference-bucket", key="model.pkl"
    )

    app.state.prometheus = start_http_server(port=settings.prometheus.port_service)

    yield


app = FastAPI(lifespan=lifespan)


@app.post("/loan_approval")
def predict_loan_approval(request: Request, client_info: UserInfo):
    try:
        with REQUEST_TIME.time():
            client_data = pd.DataFrame([client_info.model_dump()])

            processed_data = request.app.state.preprocessor.transform(client_data)
            prediction = request.app.state.model.predict(processed_data)
            probs = request.app.state.model.predict_proba(processed_data)[0]

            predicted_class = 1 if probs[1] > 0.5 else 0
            CLASS_ALLOCATION.labels(predicted_class=str(predicted_class)).inc()
            TOTAL_REQUEST.inc()

            response = "Approved" if prediction[0] == 1 else "Is not approved"
            return {"response": response}
    except Exception as e:
        return {"Error": e}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.loan.host,
        port=int(settings.loan.port_service),
    )
