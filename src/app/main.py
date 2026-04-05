import os
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

from prometheus_client import Summary, Counter

import pandas as pd

from app.config import settings
from app.utils.s3 import load_from_s3
from app.schemas.model_parameters import UserInfo

logging.basicConfig(level=logging.INFO)

REQUEST_TIME = Summary("request_processing_seconds", "Time spent processing request")
TOTAL_REQUEST = Counter("predictions_total", "Total number of predictions made")
CLASS_ALLOCATION = Counter(
    "class_distribution",
    "How often model selects class",
    ["predicted_class"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    s3_client = settings.s3.connection
    app.state.s3_client = s3_client

    app.state.preprocessor = load_from_s3(
        s3_client,
        bucket="inference-bucket",
        key="preprocessor.pkl",
    )
    app.state.model = load_from_s3(
        s3_client, bucket="inference-bucket", key="model.pkl"
    )

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
    uvicorn.run(
        "app.main:app",
        host=settings.loan.host,
        port=int(settings.s3.port_service),
        reload=True,
    )
