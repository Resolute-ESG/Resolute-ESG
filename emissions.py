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


# --- utils/scraper.py ---

import requests
from bs4 import BeautifulSoup
import re

headers = {"User-Agent": "Mozilla/5.0"}

def get_company_info(supplier_name):
    result = {
        "b_corp": False,
        "modern_slavery_statement": False
    }

    try:
        # B Corp check
        query = f"{supplier_name} site:bcorporation.uk"
        response = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
        if "bcorporation" in response.text.lower():
            result["b_corp"] = True

        # Modern Slavery check
        query2 = f"{supplier_name} Modern Slavery site:.uk"
        response2 = requests.get(f"https://www.google.com/search?q={query2}", headers=headers)
        if re.search(r"modern slavery statement", response2.text, re.IGNORECASE):
            result["modern_slavery_statement"] = True

    except Exception as e:
        print(f"Scraping error for {supplier_name}: {e}")

    return result


# --- utils/sentiment.py ---

from textblob import TextBlob
import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def analyze_sentiment(supplier_name):
    try:
        query = f"{supplier_name} ESG news"
        search_url = f"https://www.google.com/search?q={query}"
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        headlines = []
        for h in soup.find_all("h3"):
            text = h.get_text()
            if supplier_name.lower() in text.lower():
                headlines.append(text)
            if len(headlines) >= 3:
                break

        combined_text = " ".join(headlines)
        sentiment = TextBlob(combined_text).sentiment.polarity if combined_text else 0

        return sentiment, combined_text or "No relevant news found."

    except Exception as e:
        return 0, f"Sentiment analysis failed: {e}"


# --- utils/emissions.py ---

def estimate_emissions(supplier_name, spend):
    # Dummy logic using a flat emissions factor (e.g. office-based services = 0.05 kg CO2e/£1)
    # Replace this with more accurate mappings using SIC code or supplier category
    try:
        spend = float(spend)
        emissions_factor = 0.05  # kg CO2e per £1 spent (example category: professional services)
        emissions = spend * emissions_factor
        return round(emissions, 2), "Professional Services"
    except:
        return 0.0, "Unknown"
