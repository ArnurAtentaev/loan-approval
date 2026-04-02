import os
import logging
from load_dotenv import load_dotenv
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request

import pandas as pd

from src.utils.s3 import s3_connector, load_from_s3
from src.schemas.model_parameters import UserInfo
from src.utils.data_processor import DataPreprocessor

logging.basicConfig(level=logging.INFO)
load_dotenv(".env")
MINIO3_PORT = int(os.getenv("S3_PORT_EXPOSE"))
MINIO3_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
MINIO3_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")


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

    logging.info(f"Preprocessor loaded: {app.state.preprocessor}")
    logging.info("Model loaded: {app.state.model}")
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/loan_approval")
def predict_loan_approval(request: Request, client_info: UserInfo):
    try:
        client_data = pd.DataFrame([client_info.model_dump()])

        processed_data = request.app.state.preprocessor.transform(client_data)
        prediction = request.app.state.model.predict(processed_data)

        response = "Approved" if prediction[0] == 1 else "Is not approved"
        return {"response": response}
    except Exception as e:
        return {"Error": e}


if __name__ == "__main__":
    uvicorn.run("src.app.main:app", reload=True)
