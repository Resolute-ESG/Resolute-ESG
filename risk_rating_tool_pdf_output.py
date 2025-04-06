
import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Enter up to 10 suppliers and their spend. The tool will simulate ESG risk scoring and provide a downloadable PDF report.")

# Create input fields for up to 10 suppliers
supplier_inputs = []
for i in range(1, 11):
    st.subheader(f"Supplier {i}")
    name = st.text_input(f"Supplier Name {i}", key=f"name_{i}")
    spend = st.number_input(f"Spend (£) {i}", min_value=0, step=1000, key=f"spend_{i}")
    if name:
        supplier_inputs.append({"Supplier Name": name, "Spend (£)": spend})

# Proceed if any suppliers were entered
if supplier_inputs:
    df = pd.DataFrame(supplier_inputs)

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

    # Create PDF Report
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

    # Output the PDF to BytesIO for download
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    st.download_button(
        label="Download ESG Risk Report (PDF)",
        data=pdf_output,
        file_name="ESG_Risk_Assessment_Report.pdf",
        mime="application/pdf"
    )
