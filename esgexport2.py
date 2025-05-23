# ESG Live Risk Assessment Tool - Streamlit App (Manual + Upload Entry)

import streamlit as st
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from fpdf import FPDF

# -----------------------------
# Function Definitions (MUST BE FIRST)
# -----------------------------

def assess_esg_risks(df):
    results = []
    for _, row in df.iterrows():
        supplier = row.get("Supplier")
        spend = row.get("Spend", 0)
        category = row.get("Category", "Unknown")
        emissions_factor = row.get("Emissions Factor", 0.05)

        info = get_company_info(supplier)
        sentiment_score, sentiment_summary = analyze_sentiment(supplier)
        emissions = estimate_emissions(spend, emissions_factor)

        score = 0
        confidence = 0
        justification = []

        if info.get("b_corp"):
            score -= 1
            justification.append("Certified B Corp")
            confidence += 1
        if info.get("modern_slavery_statement"):
            score += 1
            justification.append("Modern Slavery Statement found")
            confidence += 1
        if sentiment_score < -0.3:
            score += 2
            justification.append("Negative ESG news sentiment")
            confidence += 1

        rag = "Green" if score <= 0 else "Amber" if score == 1 else "Red"

        results.append({
            "Supplier": supplier,
            "Spend": spend,
            "ESG Score": score,
            "RAG Rating": rag,
            "Confidence Level": confidence,
            "Justification": ", ".join(justification),
            "News Sentiment": sentiment_summary,
            "Scope 1 & 2 Emissions (kg CO2e)": emissions,
            "Category": category
        })

    return pd.DataFrame(results)


def get_company_info(supplier_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    result = {"b_corp": False, "modern_slavery_statement": False}
    try:
        b_query = f"{supplier_name} site:bcorporation.uk"
        b_response = requests.get(f"https://www.google.com/search?q={b_query}", headers=headers)
        if "bcorporation" in b_response.text.lower():
            result["b_corp"] = True

        m_query = f"{supplier_name} Modern Slavery site:.uk"
        m_response = requests.get(f"https://www.google.com/search?q={m_query}", headers=headers)
        if "modern slavery statement" in m_response.text.lower():
            result["modern_slavery_statement"] = True
    except Exception as e:
        print(f"Scraping error: {e}")
    return result


def analyze_sentiment(supplier_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        query = f"{supplier_name} ESG news"
        url = f"https://www.google.com/search?q={query}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        headlines = [h.get_text() for h in soup.find_all("h3") if supplier_name.lower() in h.get_text().lower()][:3]
        combined = " ".join(headlines)
        sentiment = TextBlob(combined).sentiment.polarity if combined else 0
        return sentiment, combined or "No relevant news found."
    except Exception as e:
        return 0, f"Sentiment error: {e}"


def estimate_emissions(spend, emissions_factor):
    try:
        return round(float(spend) * emissions_factor, 2)
    except:
        return 0.0


def export_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ESG Results')
    return output.getvalue()


def export_to_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align='C')
    pdf.ln(10)
    for _, row in df.iterrows():
        pdf.set_font("Arial", size=10)
        for col in df.columns:
            pdf.multi_cell(0, 10, txt=f"{col}: {row[col]}")
        pdf.ln(5)
    pdf_output = io.BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_bytes)
    return pdf_output.getvalue()


# -----------------------------
# Streamlit Interface
# -----------------------------

st.set_page_config(page_title="ESG Risk Rating Tool", layout="wide")

st.title("🌍 ESG Risk Rating Tool (Live Data)")
st.markdown("Enter supplier data manually or upload a file to generate live ESG risk ratings, sentiment analysis, and mitigation actions.")

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
