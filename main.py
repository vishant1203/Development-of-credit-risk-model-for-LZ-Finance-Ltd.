import streamlit as st
from prediction_helper import predict

# Page config
st.set_page_config(page_title="LZ Finance — Credit Risk", page_icon="💳", layout="wide")

# Custom CSS for nicer look
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
    }
    .card {
        background: white;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 18px rgba(50,50,93,0.08);
    }
    .muted {
        color: #6c757d;
        font-size: 0.9rem;
    }
    .title-row {
        display:flex; align-items:center; gap:12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
with st.container():
    left, right = st.columns([3,1])
    with left:
        st.markdown("<div class='title-row'> <h1 style='margin:0'>💡 LZ Finance Ltd — Credit Risk Modelling</h1></div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>Quick and explainable credit-risk estimate. Fill inputs and click Calculate.</div>", unsafe_allow_html=True)
    with right:
        st.image("https://upload.wikimedia.org/wikipedia/commons/7/72/Bank_icon.svg", width=64)

st.write("---")

# Layout: sidebar for inputs + main content for results
with st.sidebar.form(key='input_form'):
    st.header("Applicant details")
    age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
    income = st.number_input("Monthly Income (₹)", min_value=0, max_value=10_000_000, value=50_000, step=5000)
    loan_amount = st.number_input("Loan amount (₹)", min_value=0, max_value=10_000_000, value=300_000, step=5000)
    loan_tenure_months = st.slider("Loan Tenure (Months)", min_value=6, max_value=360, value=60)
    avg_dpd_per_delinquency = st.number_input('Avg DPD per delinquency', min_value=0, value=20, step=1)
    delinquency_ratio = st.number_input("Delinquency Ratio (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
    credit_utilization_ratio = st.number_input("Credit Utilization (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
    number_of_open_accounts = st.slider("Number of open accounts", min_value=1, max_value=20, value=3)

    st.markdown("---")
    st.subheader("Loan attributes")
    residence_type = st.selectbox('Residence Type', ['Owned', 'Rented', 'Mortgage'])
    loan_purpose = st.selectbox('Loan Purpose', ['Education', 'Home', 'Personal', 'Auto'])
    loan_type = st.selectbox('Loan Type', ['Secured', 'Unsecured'])

    submitted = st.form_submit_button('Calculate Risk')

# small helper
loan_to_income = loan_amount / income if income > 0 else 0

# Main results area
col1, col2 = st.columns([2,1])
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Input summary")
    st.write(f"**Loan amount:** ₹{loan_amount:,.0f}")
    st.write(f"**Monthly income:** ₹{income:,.0f}    —  Loan to income ratio: **{loan_to_income:.2f}**")
    st.write(f"**Loan Tenure:** {loan_tenure_months} months")
    st.write(f"**Avg DPD per delinquency:** {avg_dpd_per_delinquency}")
    st.write(f"**Delinquency Ratio:** {delinquency_ratio}%  •  **Credit Utilization:** {credit_utilization_ratio}%")
    st.write(f"**Open accounts:** {number_of_open_accounts}")
    st.write(f"**Residence:** {residence_type}  •  Purpose: {loan_purpose}  •  Type: {loan_type}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Quick KPIs")
    st.metric(label="Loan / Income", value=f"{loan_to_income:.2f}")
    st.metric(label="Open accounts", value=f"{number_of_open_accounts}")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("\n")

# Calculate and show results if submitted
if submitted:
    try:
        probability, credit_score, rating = predict(
            age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, number_of_open_accounts,
            residence_type, loan_purpose, loan_type,
        )

        # Ensure probability is in [0,1]
        probability = max(0.0, min(1.0, float(probability)))

        # Result cards
        rcol1, rcol2, rcol3 = st.columns(3)
        with rcol1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Default probability")
            st.metric(label="Probability", value=f"{probability:.2%}")
            # progress bar for visual
            st.progress(int(probability * 100))
            st.markdown("</div>", unsafe_allow_html=True)

        with rcol2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Credit score")
            st.metric(label="Score", value=str(credit_score))
            st.caption("Higher is better — thresholds depend on your model")
            st.markdown("</div>", unsafe_allow_html=True)

        with rcol3:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Rating")
            st.metric(label="Risk Rating", value=str(rating))
            st.markdown("</div>", unsafe_allow_html=True)

        # Show short textual explanation
        with st.expander("Model explanation & what to do next"):
            st.write(
                "The model uses applicant credit behaviour and loan attributes. A higher default probability suggests lender caution — consider higher interest, collateral, or denial. For candidates close to your acceptance threshold, request additional documents or guarantor."
            )

        # Optional: download results as CSV
        import pandas as pd
        out = pd.DataFrame([{
            'age': age,
            'income': income,
            'loan_amount': loan_amount,
            'loan_tenure_months': loan_tenure_months,
            'avg_dpd_per_delinquency': avg_dpd_per_delinquency,
            'delinquency_ratio': delinquency_ratio,
            'credit_utilization_ratio': credit_utilization_ratio,
            'number_of_open_accounts': number_of_open_accounts,
            'residence_type': residence_type,
            'loan_purpose': loan_purpose,
            'loan_type': loan_type,
            'default_probability': probability,
            'credit_score': credit_score,
            'rating': rating
        }])
        csv = out.to_csv(index=False).encode('utf-8')
        st.download_button('Download result (CSV)', csv, file_name='credit_risk_result.csv', mime='text/csv')

    except Exception as e:
        st.error(f"Error while predicting: {e}")

st.write("---")
st.markdown('<div class="muted">Development of Credit Risk Model for LZ Finance Ltd. — copyright by LIVIS AI </div>', unsafe_allow_html=True)


# import streamlit as st
# from prediction_helper import predict
#
# st.set_page_config(page_title="LZ Finance Ltd: Credit Risk Modelling", page_icon="")
# st.title("LZ Finance Ltd: Credit Risk Modelling")
#
# #create rows for three columns each
# row1=st.columns(3)
# row2=st.columns(3)
# row3=st.columns(3)
# row4=st.columns(3)
#
# #Assign inputs to first row with default values
# with row1[0]:
#     age=st.number_input("Age", min_value=18, max_value=100, step=1, value=20)
# with row1[1]:
#     income=st.number_input("Income", min_value=0, max_value=1200000, value=10000, step=2000)
# with row1[2]:
#     loan_amount=st.number_input("Loan amount", min_value=0, max_value=6000000)
#
# loan_to_income=loan_amount/income if income>0 else 0
# with row2[0]:
#     st.text("Loan to Income Ratio")
#     st.text(f"{loan_to_income:.2f}")
# with row2[1]:
#     loan_tenure_months=st.number_input("Loan Tenure (Months)", min_value=1, max_value=360)
# with row2[2]:
#     avg_dpd_per_delinquency=st.number_input('Avg DPD', min_value=0, value=20)
#
# with row3[0]:
#     delinquency_ratio=st.number_input("Delinquency Ratio", min_value=0, max_value=100, step=1, value=30)
# with row3[1]:
#     credit_utilization_ratio=st.number_input("Credit Utilization (%)", min_value=0, max_value=100, step=1)
# with row3[2]:
#     number_of_open_accounts=st.number_input("Number of open accounts", min_value=1, max_value=4, step=1)
#
# with row4[0]:
#     residence_type=st.selectbox('Residence Type', ['Owned', 'Rented', 'Mortgage'])
# with row4[1]:
#     loan_purpose=st.selectbox('Loan Purpose', ['Education', 'Home', 'Personal', 'Auto'])
# with row4[2]:
#     loan_type=st.selectbox('Loan Type', ['Secured', 'Unsecured'])
#
#
# #      X_train_encoded.columns---> Index(['number_of_open_accounts', 'credit_utilization_ratio', 'age',
# #      'loan_tenure_months', 'loan_to_income', 'delinquency_ratio',
# #      'avg_dpd_per_delinquency', 'residence_type_Owned',
# #      'residence_type_Rented', 'loan_purpose_Education', 'loan_purpose_Home',
# #      'loan_purpose_Personal', 'loan_type_Unsecured']
#
# if st.button('Calculate Risk'):
#     probability,credit_score, rating=predict(age,income, loan_amount, loan_tenure_months,avg_dpd_per_delinquency,
#                                              delinquency_ratio,credit_utilization_ratio, number_of_open_accounts,
#                                              residence_type,loan_purpose,loan_type)
#
#     st.write(f" Default Probability --> {probability:.2%}")
#     st.write(f"Credit Score-->{credit_score}")
#     st.write(f" Rating -->{rating}")
#
# st.markdown('Development of Credit Risk Model for LZ Finance Ltd.-copyright by LIVIS AI Infotech')

