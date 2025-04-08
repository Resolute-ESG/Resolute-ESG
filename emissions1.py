# ESG Live Risk Assessment Tool - Streamlit App (Manual Entry)

import streamlit as st
import pandas as pd
from esg_engine import assess_esg_risks
from exporters import export_to_excel, export_to_pdf

st.set_page_config(page_title="ESG Risk Rating Tool", layout="wide")

st.title("🌍 ESG Risk Rating Tool (Live Data)")
st.markdown("Manually enter supplier data to generate live ESG risk ratings, sentiment analysis, and mitigation actions.")

# Based on UK Government conversion factors (example values, adjust as needed)
emissions_categories = {
    "Professional Services": 0.05,
    "Construction": 0.12,
    "IT Equipment": 0.18,
    "Transport Services": 0.15,
    "Facilities Management": 0.10,
    "Healthcare Products": 0.14,
    "Utilities": 0.22,
    "Food and Catering": 0.25
}

supplier_data = []
supplier_count = st.number_input("How many suppliers would you like to assess?", min_value=1, max_value=20, step=1)

st.subheader("📝 Enter Supplier Details")

for i in range(supplier_count):
    with st.expander(f"Supplier {i+1}"):
        name = st.text_input(f"Supplier Name {i+1}", key=f"name_{i}")
        spend = st.number_input(f"Spend (£) {i+1}", min_value=0.0, key=f"spend_{i}")
        category = st.selectbox(f"Emissions Category {i+1}", list(emissions_categories.keys()), key=f"category_{i}")
        supplier_data.append({"Supplier": name, "Spend": spend, "Category": category})

if st.button("Run ESG Risk Assessment"):
    with st.spinner("Assessing ESG risks using live data sources..."):
        input_df = pd.DataFrame(supplier_data)
        input_df["Emissions Factor"] = input_df["Category"].map(emissions_categories)
        result_df = assess_esg_risks(input_df)
        st.success("Assessment Complete!")

        st.subheader("✅ ESG Risk Results")
        st.dataframe(result_df)

        st.download_button("📥 Download as Excel", export_to_excel(result_df), file_name="esg_risk_assessment.xlsx")
        st.download_button("📄 Download PDF Report", export_to_pdf(result_df), file_name="esg_risk_assessment.pdf")


# --- esg_engine.py ---

import pandas as pd
from utils.scraper import get_company_info
from utils.sentiment import analyze_sentiment
from utils.emissions import estimate_emissions

def assess_esg_risks(df):
    results = []
    for _, row in df.iterrows():
        supplier = row.get("Supplier")
        spend = row.get("Spend", 0)
        category = row.get("Category", "Unknown")
        emissions_factor = row.get("Emissions Factor", 0.05)

        # Scrape and analyze supplier info
        info = get_company_info(supplier)
        sentiment_score, sentiment_summary = analyze_sentiment(supplier)
        emissions = estimate_emissions(spend, emissions_factor)

        # Example logic for scoring
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

        # RAG classification
        if score <= 0:
            rag = "Green"
        elif score == 1:
            rag = "Amber"
        else:
            rag = "Red"

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


# --- utils/emissions.py ---

def estimate_emissions(spend, emissions_factor):
    try:
        spend = float(spend)
        emissions = spend * emissions_factor
        return round(emissions, 2)
    except:
        return 0.0
