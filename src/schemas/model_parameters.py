from pydantic import BaseModel


class UserInfo(BaseModel):
    Applicant_Income: float
    Coapplicant_Income: float
    Employment_Status: str
    Age: float
    Dependents: int
    Credit_Score: float
    Existing_Loans: int
    DTI_Ratio: float
    Savings: float
    Collateral_Value: float
    Loan_Amount: float
    Loan_Term: float
    Property_Area: str

    Marital_Status: str
    Education_Level: str
    Gender: str
    Loan_Purpose: str
