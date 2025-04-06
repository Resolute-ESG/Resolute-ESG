
import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Upload a file with supplier name and spend. The tool will simulate ESG risk scoring and provide a downloadable PDF report.")

# File uploader
uploaded_file = st.file_uploader("Upload Supplier File (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read the uploaded file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Ensure required columns exist
        if "Supplier Name" not in df.columns or "Spend (£)" not in df.columns:
            st.error("Uploaded file must contain 'Supplier Name' and 'Spend (£)' columns.")
        else:
            # Simulated ESG Risk Assessment Logic
            def assess_risk(row):
                score = 0
                if row["Spend (£)"] > 1000000:
                    score += 1
                if "green" in row["Supplier Name"].lower() or "eco" in row["Supplier Name"].lower():
                    score += 1
                if "oil" in row["Supplier Name"].lower() or "chemical" in row["Supplier Name"].lower():
                    score -= 2

                if score >= 2:
                    return "Low"
                elif score >= 0:
                    return "Medium"
                else:
                    return "High"

            df["ESG Risk Rating"] = df.apply(assess_risk, axis=1)

            st.success("Suppliers assessed successfully!")
            st.dataframe(df)

            # Generate PDF Report
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.set_title("ESG Risk Assessment Report")
            pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align="C")
            pdf.ln(10)

            for _, row in df.iterrows():
                pdf.cell(200, 10, txt=f"Supplier: {row['Supplier Name']}", ln=True)
                pdf.cell(200, 10, txt=f"Spend: £{int(row['Spend (£)']):,}", ln=True)
                pdf.cell(200, 10, txt=f"ESG Risk Rating: {row['ESG Risk Rating']}", ln=True)
                pdf.ln(5)

            pdf_output = io.BytesIO()
            pdf.output(pdf_output)
            pdf_output.seek(0)

            st.download_button(
                label="Download ESG Risk Report (PDF)",
                data=pdf_output,
                file_name="ESG_Risk_Assessment_Report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
