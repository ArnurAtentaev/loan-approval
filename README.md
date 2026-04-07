<h1 align="center">Loan Approval ML System</h1>
<h2>Project Description</h2>
This project solves the problem of binary classification - whether to approve a loan or not.
<p>
The system takes customer data, processes it through a calendar preprocessing and makes a decision:
<ul>
<li>✅ Approved</li>
<li>❌ Is not approved</li>
</ul>
</p>

<h2>Source characteristics:</h2>
```
Applicant_Income: float
Coapplicant_Income: float
Employment_Status: ["Salaried", "Contract", "Unemployed", "Self-employed"]
Age: float
Marital_Status: ["Married", "Single"]
Dependents: int
Credit_Score: float
Existing_Loans: int
DTI_Ratio: float
Savings: float
Collateral_Value: float
Loan_Amount: float
Loan_Term: float
Loan_Purpose: ["Car", "Home", "Personal", "Education", "Business"]
Property_Area: ["Rural", "Urban", "Semiurban"]
Education_Level: ["Not Graduate", "Graduate"]
Gender: ["Male", "Female"]
```

<h2>Feature Engineering</h2>
<p>
The project implements a DataPreprocessor caste class that performs data preparation.
</p>
<p>
Used as Pipeline:
The class is designed as a pre-trained preprocessing pipeline that can be applied to new data before it is submitted to the model. This ensures:
</p>
<p>
Uniform Feature Processing
Generation of new, informative cues
Convert categorical and order data
Data preparation for the model in production mode
</p>
<p>
This way, DataPreprocessor can be easily integrated into API or other ML-PIPs to automatically preprocess customers' input data before forecasting.
</p>
<h3>Generated Traits</h3>
<ul>
<li>total_income - total income</li>
<li>approximate_loan_amount - adjusted loan size</li>
<li>payment_capacity - customer’s ability to pay</li>
<li>collateral_ratio - ratio of collateral to credit</li>
<li>income_to_loan - ratio of income to loan amount</li>
<li>risk_score - customer risk</li>
</ul>
<h3>Character encoding</h3>
<ul>
<li>One-Hot Encoding:</li>
```["Marital_Status", "Education_Level", "Gender", "Loan_Purpose"]```
<li>Ordinal Encoding:</li>
```Property_Area: ["Rural", "Semiurban", "Urban"]```
<li>Target Encoding:</li>
```Employment_Status```
</ul>
<h3>Final set of traits</h3>
```
[
 'Applicant_Income', 'Coapplicant_Income', 'Employment_Status', 'Age',
 'Dependents', 'Credit_Score', 'Existing_Loans', 'DTI_Ratio', 'Savings',
 'Collateral_Value', 'Loan_Amount', 'Loan_Term', 'Property_Area',
 'total_income', 'approximate_loan_amount', 'payment_capacity',
 'collateral_ratio', 'income_to_loan', 'risk_score',
 'Marital_Status_Married', 'Marital_Status_Single',
 'Education_Level_Graduate', 'Education_Level_Not Graduate',
 'Gender_Female', 'Gender_Male',
 'Loan_Purpose_Business', 'Loan_Purpose_Car',
 'Loan_Purpose_Education', 'Loan_Purpose_Home',
 'Loan_Purpose_Personal'
]
```
<p>
Also to correct the imbalance of classes, I used SMOTE, which was able to raise the value of the metric complex by 3-5 percent.
</p>
<h2>Model</h2>
<h3>Experiments have been conducted between models:</h3>
<ul>
<li>Linear Regression</li>
<li>SVM</li>
<li>Random Forest</li>
<li>Gradient Boosting</li>
</ul>
<p>The best score was in the gradient busting model - XGBClassifier</p>