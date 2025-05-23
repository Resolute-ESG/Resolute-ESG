# ESG Live Risk Assessment Tool - Streamlit App (Scaffold)

import streamlit as st
import pandas as pd
from esg_engine import assess_esg_risks
from exporters import export_to_excel, export_to_pdf

st.set_page_config(page_title="ESG Risk Rating Tool", layout="wide")

st.title("🌍 ESG Risk Rating Tool (Live Data)")
st.markdown("Upload your supplier list to generate live ESG risk ratings, sentiment analysis, and mitigation actions.")

uploaded_file = st.file_uploader("Upload Supplier List (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📋 Supplier Preview")
        st.dataframe(df.head())

        if st.button("Run ESG Risk Assessment"):
            with st.spinner("Assessing ESG risks using live data sources..."):
                result_df = assess_esg_risks(df)
                st.success("Assessment Complete!")

                st.subheader("✅ ESG Risk Results")
                st.dataframe(result_df)

                st.download_button("📥 Download as Excel", export_to_excel(result_df), file_name="esg_risk_assessment.xlsx")
                st.download_button("📄 Download PDF Report", export_to_pdf(result_df), file_name="esg_risk_assessment.pdf")

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
else:
    st.info("Please upload a file to begin.")


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

        # Scrape and analyze supplier info
        info = get_company_info(supplier)
        sentiment_score, sentiment_summary = analyze_sentiment(supplier)
        emissions, category = estimate_emissions(supplier, spend)

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
