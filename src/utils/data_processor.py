import numpy as np
import pandas as pd

from category_encoders import TargetEncoder
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from imblearn.over_sampling import SMOTE


class DataPreprocessor:
    def __init__(
        self,
        cols_for_ohe: list[str],
        ordinal_cols: list[str],
        ordinal_cat: list[str],
        target_cols: list[str],
    ):
        self.cols_for_ohe = cols_for_ohe
        self.ordinal_cols = ordinal_cols
        self.ordinal_cat = ordinal_cat
        self.target_cols = target_cols

    def feature_extraction(self, data: pd.DataFrame):
        data["total_income"] = data["Applicant_Income"] + data["Coapplicant_Income"]
        data["approximate_loan_amount"] = data["Loan_Amount"] / (
            data["Existing_Loans"] + 1
        )
        data["payment_capacity"] = ((data["total_income"]) + data["Savings"]) / (
            data["Loan_Amount"]
            * (data["Existing_Loans"] + 1)
            / (data["Credit_Score"] + 1)
        )
        data["collateral_ratio"] = data["Collateral_Value"] / (data["Loan_Amount"] + 1)
        data["income_to_loan"] = (data["total_income"]) / (data["Loan_Amount"] + 1)
        data["risk_score"] = (data["DTI_Ratio"] * data["Loan_Amount"]) / (
            data["Credit_Score"] + 1
        )
        return data

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series):
        X_train = self.feature_extraction(X_train)

        self.ohe_scaler = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        self.ohe_scaler.fit(X_train[self.cols_for_ohe])
        ohe_cols = self.ohe_scaler.get_feature_names_out(self.cols_for_ohe)
        X_ohe = pd.DataFrame(
            self.ohe_scaler.transform(X_train[self.cols_for_ohe]),
            columns=ohe_cols,
            index=X_train.index,
        )
        X_train = pd.concat([X_train.drop(columns=self.cols_for_ohe), X_ohe], axis=1)

        self.oe_scaler = OrdinalEncoder(categories=[self.ordinal_cat])
        self.oe_scaler.fit(X_train[self.ordinal_cols])
        X_train[self.ordinal_cols] = self.oe_scaler.transform(
            X_train[self.ordinal_cols]
        )

        self.target_enc = TargetEncoder(smoothing=5)
        self.target_enc.fit(X_train[self.target_cols], y_train)
        X_train[self.target_cols] = self.target_enc.transform(X_train[self.target_cols])

        return X_train, y_train

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = self.feature_extraction(X)

        encoded_ohe = self.ohe_scaler.transform(X[self.cols_for_ohe])
        ohe_cols = self.ohe_scaler.get_feature_names_out(self.cols_for_ohe)
        X = pd.concat(
            [
                X.drop(columns=self.cols_for_ohe),
                pd.DataFrame(encoded_ohe, columns=ohe_cols, index=X.index),
            ],
            axis=1,
        )

        X[self.ordinal_cols] = self.oe_scaler.transform(X[self.ordinal_cols])

        X[self.target_cols] = self.target_enc.transform(X[self.target_cols])
        return X

    def resample(self, X: pd.DataFrame, y: pd.Series):
        smote = SMOTE(random_state=42)
        X_res, y_res = smote.fit_resample(X, y)
        return X_res, y_res
