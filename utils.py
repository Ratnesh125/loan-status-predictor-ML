import numpy as np 
import joblib 


def preprocessdata(Gender, Married, Education, Self_Employed, ApplicantIncome,
       CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History,
       Property_Area,Dependents):
    test_data = [[Gender, Married, Education, Self_Employed, ApplicantIncome,
       CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History,
       Property_Area,Dependents] ]  
    trained_model = joblib.load("model.pkl") 
    prediction = trained_model.predict(test_data) 

    return prediction 
