import os
from load_dotenv import load_dotenv

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from xgboost import XGBClassifier

from src.utils.data_processor import DataPreprocessor
from src.utils.s3 import s3_connector, save_object

load_dotenv(".env")

MINIO3_PORT = os.getenv("S3_PORT_EXPOSE")
MINIO3_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
MINIO3_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")


df = pd.read_csv("dataframes/raw_data/loan_approval_data.csv")
df.drop(["Applicant_ID", "Employer_Category"], inplace=True, axis=1)

cols_for_ohe = ["Marital_Status", "Education_Level", "Gender", "Loan_Purpose"]
ordinal_cols = ["Property_Area"]
ordinal_cat = ["Rural", "Semiurban", "Urban"]
target_cols = ["Employment_Status"]

X = df.drop(columns=["Loan_Approved"])
y = df["Loan_Approved"].map({"No": 0, "Yes": 1})

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42,
)

preprocessor = DataPreprocessor(
    cols_for_ohe=cols_for_ohe,
    ordinal_cols=ordinal_cols,
    ordinal_cat=ordinal_cat,
    target_cols=target_cols,
)
X_train_processed, y_train_processed = preprocessor.fit(X_train, y_train)
X_train_res, y_train_res = preprocessor.resample(X_train_processed, y_train_processed)
X_test_processed = preprocessor.transform(X_test)

scale_pos_weight = len(np.where(y_train == 0)) / len(np.where(y_train == 1))
model = XGBClassifier(
    device="cuda:0",
    learning_rate=0.05,
    n_estimators=800,
    max_depth=4,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    reg_alpha=0.6,
    scale_pos_weight=scale_pos_weight,
    tree_method="hist",
)
model = model.fit(X_train_res, y_train_res)

client = s3_connector(
    client_name="s3",
    port=MINIO3_PORT,
    access_key_id=MINIO3_ACCESS_KEY_ID,
    secret_access_key=MINIO3_SECRET_ACCESS_KEY,
)
save_object(client, preprocessor, "inference-bucket", "preprocessor.pkl")
save_object(client, model, "inference-bucket", "model.pkl")
