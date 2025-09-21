import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

#Path to saved model and its component
MODEL_PATH='artifacts/model_data.joblib'

#Load Model and its components
model_data=joblib.load(MODEL_PATH)
model=model_data['model']
scaler=model_data['scaler']
features=model_data['features']
cols_to_scale=model_data['cols_to_scale']

def prepare_input(age,income, loan_amount, loan_tenure_months,avg_dpd_per_delinquency,
                                             delinquency_ratio,credit_utilization_ratio, number_of_open_accounts,
                                             residence_type,loan_purpose,loan_type):
    #create dictionary with user input values and dummy values for missing featurs
    input_data={
        'age':age,
        'loan_to_income':loan_amount/income,
        'loan_tenure_months':loan_tenure_months,
        'avg_dpd_per_delinquency':avg_dpd_per_delinquency,
        'delinquency_ratio':delinquency_ratio,
        'credit_utilization_ratio':credit_utilization_ratio,
        'number_of_open_accounts':number_of_open_accounts,
        'residence_type_Owned':1 if residence_type=='Owned' else 0,
        'residence_type_Rented': 1 if residence_type == 'Rented' else 0,
        'loan_purpose_Education': 1 if loan_purpose=='Education' else 0,
        'loan_purpose_Home': 1 if loan_purpose == 'Home' else 0,
        'loan_purpose_Personal': 1 if loan_purpose == 'Personal' else 0,
        'loan_type_Unsecured':1 if loan_type=='Unsecured' else 0,
        ##additional dummy fields just for scaling purpose
        'number_of_closed_accounts':1, #dummy value
        'enquiry_count':1, #dummy value
        'number_of_dependants':1, #dummy value
        'years_at_current_address':1,#dummy value
        'sanction_amount':1, #dummy value
        'processing_fee':1, #dummy value
        'gst':1, #dummy value
        'net_disbursement':1, #dummy value
        'principal_outstanding':1, #dummy
        'enquiry_count':1, #dummy value
        'bank_balance_at_application': 1#dummy value
    }
    #ensure all columns for features and columns to scale arepresent
    df=pd.DataFrame([input_data])

    #ensure only required columns for scaling are scaled
    df[cols_to_scale]=scaler.transform(df[cols_to_scale])

    #ensuredataframe contain only features expected by the model
    df=df[features]

    return df


def predict(age,income, loan_amount, loan_tenure_months,avg_dpd_per_delinquency,
                                             delinquency_ratio,credit_utilization_ratio, number_of_open_accounts,
                                             residence_type,loan_purpose,loan_type):
    #input df
    input_df=prepare_input(age,income, loan_amount, loan_tenure_months,avg_dpd_per_delinquency,
                                             delinquency_ratio,credit_utilization_ratio, number_of_open_accounts,
                                             residence_type,loan_purpose,loan_type)

    probability,credit_score, rating=calculate_credit_score(input_df)
    return probability, credit_score, rating


def calculate_credit_score(input_df, base_score=300, scale_length=600):
    x=np.dot(input_df.values, model.coef_.T)+model.intercept_


    #Apply logistic function to calculate probability
    default_probability=1/(1+np.exp(-x))

    non_default_probability=1-default_probability

    #convert probability into credit score, scaled to fit within range 300 to 900
    credit_score=base_score+non_default_probability.flatten()*scale_length

    #determine rating category based on credit score
    def get_rating(score):
        if 300<=score<500:
            return 'Poor'
        elif 500<=score<600:
            return 'Average'
        elif 650<=score<750:
            return'Good'
        elif 750<=score<900:
            return 'Excellent'
        else:
            return 'Undefined'

    rating=get_rating(credit_score[0])

    return default_probability.flatten()[0], int(credit_score[0]), rating

