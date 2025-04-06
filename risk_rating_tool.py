
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Upload your supplier list to receive a downloadable ESG risk report, including assessments for SBTi alignment, London Living Wage accreditation, and B Corp certification.")

uploaded_file = st.file_uploader("Upload Supplier File (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Sample ESG Scoring Logic (Mock)
        def assess_risk(row):
            score = 0
            if row.get("SBTi Aligned") == "Yes":
                score += 1
            if row.get("LLW Accredited") == "Yes":
                score += 1
            if row.get("B Corp Certified") == "Yes":
                score += 1
            if row.get("Sentiment") == "Negative":
                score -= 2
            elif row.get("Sentiment") == "Neutral":
                score -= 1

            if score >= 2:
                return "Low"
            elif score >= 0:
                return "Medium"
            else:
                return "High"

        df["ESG Risk Rating"] = df.apply(assess_risk, axis=1)

        st.success("File processed successfully!")
        st.dataframe(df)

        # Download button
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='ESG Assessment')
        st.download_button(label="Download ESG Risk Report",
                           data=output.getvalue(),
                           file_name="ESG_Risk_Report.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Error processing file: {e}")
