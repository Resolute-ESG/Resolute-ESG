# ESG Live Risk Assessment Tool - Streamlit App (Manual + Upload Entry)

import streamlit as st
import pandas as pd
import io
from esg_engine import assess_esg_risks
from exporters import export_to_excel, export_to_pdf

st.set_page_config(page_title="ESG Risk Rating Tool", layout="wide")

st.title("🌍 ESG Risk Rating Tool (Live Data)")
st.markdown("Enter supplier data manually or upload a file to generate live ESG risk ratings, sentiment analysis, and mitigation actions.")

# Based on UK Government GHG Conversion Factors for Company Reporting (example values for 2023)
emissions_categories = {
    "Professional Services": 0.045,
    "Construction": 0.134,
    "IT Equipment": 0.156,
    "Transport Services": 0.123,
    "Facilities Management": 0.111,
    "Healthcare Products": 0.149,
    "Utilities": 0.210,
    "Food and Catering": 0.232,
    "Office Equipment": 0.095,
    "Cleaning Services": 0.102,
    "Printing and Paper": 0.141
}

entry_mode = st.radio("Choose data entry method:", ("Manual Entry", "Upload CSV/Excel"))

supplier_data = []

if entry_mode == "Manual Entry":
    supplier_count = st.number_input("How many suppliers would you like to assess?", min_value=1, max_value=20, step=1)

    st.subheader("📝 Enter Supplier Details")
    for i in range(supplier_count):
        with st.expander(f"Supplier {i+1}"):
            name = st.text_input(f"Supplier Name {i+1}", key=f"name_{i}")
            spend = st.number_input(f"Spend (£) {i+1}", min_value=0.0, key=f"spend_{i}")
            category = st.selectbox(f"Emissions Category {i+1}", list(emissions_categories.keys()), key=f"category_{i}")
            supplier_data.append({"Supplier": name, "Spend": spend, "Category": category})

elif entry_mode == "Upload CSV/Excel":
    uploaded_file = st.file_uploader("Upload Supplier List (CSV or Excel)", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("📋 Uploaded Supplier Preview")
            st.dataframe(df.head())

            if "Supplier" in df.columns and "Spend" in df.columns and "Category" in df.columns:
                supplier_data = df.to_dict(orient="records")
            else:
                st.warning("Uploaded file must contain 'Supplier', 'Spend', and 'Category' columns.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

if supplier_data and st.button("Run ESG Risk Assessment"):
    with st.spinner("Assessing ESG risks using live data sources..."):
        input_df = pd.DataFrame(supplier_data)
        input_df["Emissions Factor"] = input_df["Category"].map(emissions_categories)
        result_df = assess_esg_risks(input_df)
        st.success("Assessment Complete!")

        st.subheader("✅ ESG Risk Results")
        st.dataframe(result_df)

        excel_data = export_to_excel(result_df)
        pdf_data = export_to_pdf(result_df)

        st.download_button("📥 Download as Excel", data=excel_data, file_name="esg_risk_assessment.xlsx")
        st.download_button("📄 Download PDF Report", data=pdf_data, file_name="esg_risk_assessment.pdf")


# --- exporters.py ---

import pandas as pd
import io
from fpdf import FPDF

def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ESG Results')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

def export_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align='C')
    pdf.ln(10)

    for index, row in df.iterrows():
        pdf.set_font("Arial", size=10)
        for col in df.columns:
            text = f"{col}: {row[col]}"
            pdf.multi_cell(0, 10, txt=text)
        pdf.ln(5)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()
