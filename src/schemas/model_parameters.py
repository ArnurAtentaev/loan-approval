from typing import Literal
from pydantic import BaseModel


class UserInfo(BaseModel):
    Applicant_Income: float
    Coapplicant_Income: float
    Employment_Status: Literal["Salaried", "Contract", "Unemployed", "Self-employed"]
    Age: float
    Marital_Status: Literal["Married", "Single"]
    Dependents: int
    Credit_Score: float
    Existing_Loans: int
    DTI_Ratio: float
    Savings: float
    Collateral_Value: float
    Loan_Amount: float
    Loan_Term: float
    Loan_Purpose: Literal["Car", "Home", "Personal", "Education", "Business"]
    Property_Area: Literal["Rural", "Urban", "Semiurban"]
    Education_Level: Literal["Not Graduate", "Graduate"]
    Gender: Literal["Male", "Female"]
