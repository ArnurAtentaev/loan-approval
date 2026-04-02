import os
import logging
from load_dotenv import load_dotenv
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

from prometheus_client import start_http_server, Summary, Counter

import pandas as pd

from src.utils.s3 import s3_connector, load_from_s3
from src.schemas.model_parameters import UserInfo

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")
MINIO3_PORT = os.getenv("S3_PORT_EXPOSE")
MINIO3_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
MINIO3_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")

PROMETHEUS_PORT_EXPOSE = os.getenv("PROMETHEUS_PORT_EXPOSE")

REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")
TOTAL_REQUEST = Counter("predictions_total", "Total number of predictions made")
CLASS_ALLOCATION = Counter(
    "class_distribution",
    "How often model selects class",
    ["predicted_class"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    s3_conn = s3_connector(
        client_name="s3",
        port=MINIO3_PORT,
        access_key_id=MINIO3_ACCESS_KEY_ID,
        secret_access_key=MINIO3_SECRET_ACCESS_KEY,
    )
    app.state.preprocessor = load_from_s3(
        s3_conn, bucket="inference-bucket", key="preprocessor.pkl"
    )
    app.state.model = load_from_s3(s3_conn, bucket="inference-bucket", key="model.pkl")

    start_http_server(PROMETHEUS_PORT_EXPOSE)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/loan_approval")
def predict_loan_approval(request: Request, client_info: UserInfo):
    try:
        with REQUEST_TIME.time():
            client_data = pd.DataFrame([client_info.model_dump()])

            processed_data = request.app.state.preprocessor.transform(client_data)
            prediction = request.app.state.model.predict(processed_data)
            probs = request.app.state.model.predict.predict_proba(processed_data)[0]

            predicted_class = 1 if probs[1] > 0.5 else 0
            CLASS_ALLOCATION.labels(predicted_class=str(predicted_class)).inc()
            TOTAL_REQUEST.inc()

            response = "Approved" if prediction[0] == 1 else "Is not approved"
            return {"response": response}
    except Exception as e:
        return {"Error": e}


if __name__ == "__main__":
    uvicorn.run("src.app.main:app", reload=True)
