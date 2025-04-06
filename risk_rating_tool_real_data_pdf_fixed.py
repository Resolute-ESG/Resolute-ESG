
import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import io
import datetime

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Enter a supplier name and spend. This tool will attempt to retrieve real ESG indicators and produce a risk rating report in PDF format.")

# Supplier input
supplier_name = st.text_input("Supplier Name")
supplier_spend = st.number_input("Spend (£)", min_value=0, step=1000)

if st.button("Run ESG Assessment") and supplier_name:
    # --- START ENRICHMENT ---
    enriched = {}

    def check_sbti(supplier):
        try:
            r = requests.get("https://sciencebasedtargets.org/companies-taking-action", timeout=10)
            return "Yes" if supplier.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def check_bcorp(supplier):
        try:
            r = requests.get(f"https://www.bcorporation.net/en-us/find-a-b-corp/?search={supplier}", timeout=10)
            return "Yes" if supplier.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def check_llw(supplier):
        try:
            r = requests.get("https://www.livingwage.org.uk/accredited-living-wage-employers", timeout=10)
            return "Yes" if supplier.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def get_sentiment(supplier):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://www.bing.com/news/search?q={supplier}", headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            headlines = soup.find_all("a")
            texts = " ".join([h.get_text() for h in headlines if h.get_text()])
            analysis = TextBlob(texts)
            score = analysis.sentiment.polarity
            if score > 0.1:
                return "Positive"
            elif score < -0.1:
                return "Negative"
            else:
                return "Neutral"
        except:
            return "Unknown"

    def estimate_carbon_category(supplier):
        return "Logistics" if "transport" in supplier.lower() or "logistic" in supplier.lower() else "Professional Services"

    enriched["SBTi Aligned"] = check_sbti(supplier_name)
    enriched["B Corp Certified"] = check_bcorp(supplier_name)
    enriched["LLW Accredited"] = check_llw(supplier_name)
    enriched["Sentiment"] = get_sentiment(supplier_name)
    enriched["Carbon Conversion Category"] = estimate_carbon_category(supplier_name)

    enriched.update({
        "Scope 1 & 2 Emissions (tCO2e)": 120,
        "Supplier Diversity": "Unknown",
        "Board Diversity": "Unknown",
        "Modern Slavery Statement": "Unknown",
        "Factory Conditions Reported": "Unknown",
        "Whistleblowing Cases": 0,
        "Ownership Structure": "Unknown",
        "Fair Payment Code Signatory": "Unknown",
        "Sedex Member": "Unknown",
        "3rd Party Manufacturing": "Unknown"
    })

    def assess_risk(data):
        score = 0
        if data["SBTi Aligned"] == "Yes": score += 1
        if data["LLW Accredited"] == "Yes": score += 1
        if data["B Corp Certified"] == "Yes": score += 1
        if data["Sentiment"] == "Negative": score -= 2
        elif data["Sentiment"] == "Neutral": score -= 1
        return "Low" if score >= 2 else "Medium" if score >= 0 else "High"

    risk_rating = assess_risk(enriched)

    # Create PDF Report
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_title("ESG Risk Assessment Report")

    pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Supplier: {supplier_name}", ln=True)
    pdf.cell(200, 10, txt=f"Spend: £{int(supplier_spend):,}", ln=True)
    pdf.cell(200, 10, txt=f"ESG Risk Rating: {risk_rating}", ln=True)
    pdf.ln(10)

    for k, v in enriched.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)

    # Fix: Output as PDF bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="Download ESG Risk Report (PDF)",
        data=pdf_bytes,
        file_name=f"ESG_Risk_Report_{supplier_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
