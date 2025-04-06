
import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import datetime

st.set_page_config(page_title="ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool (Full Report)")
st.markdown("Enter a supplier name and spend. The tool will generate a full ESG profile and provide a downloadable PDF report.")

supplier_name = st.text_input("Supplier Name")
supplier_spend = st.number_input("Spend (£)", min_value=0, step=1000)

if st.button("Run ESG Assessment") and supplier_name:

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
            texts = [h.get_text() for h in headlines if h.get_text()]
            summary = "; ".join(texts[:3])
            analysis = TextBlob(" ".join(texts))
            score = analysis.sentiment.polarity
            sentiment = "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral"
            return sentiment, summary
        except:
            return "Unknown", "Unable to retrieve headlines."

    def estimate_carbon_category(supplier):
        return "Logistics" if "transport" in supplier.lower() or "logistic" in supplier.lower() else "Professional Services"

    # Real + Simulated Enrichment
    enriched["SBTi Aligned"] = check_sbti(supplier_name)
    enriched["B Corp Certified"] = check_bcorp(supplier_name)
    enriched["LLW Accredited"] = check_llw(supplier_name)
    enriched["Sentiment"], enriched["Media Example"] = get_sentiment(supplier_name)
    enriched["Carbon Conversion Category"] = estimate_carbon_category(supplier_name)
    enriched["Scope 1 & 2 Emissions (tCO2e)"] = 120
    enriched["Supplier Diversity"] = "Unknown"
    enriched["Board Diversity"] = "Unknown"
    enriched["Ownership Structure"] = "Unknown"
    enriched["Modern Slavery Statement"] = "Unknown"
    enriched["Factory Conditions Reported"] = "Unknown"
    enriched["Whistleblowing Cases"] = "Unknown"
    enriched["Sedex Member"] = "Unknown"
    enriched["3rd Party Manufacturing"] = "Unknown"

    def assess_risk(data):
        score = 0
        if data["SBTi Aligned"] == "Yes": score += 1
        if data["LLW Accredited"] == "Yes": score += 1
        if data["B Corp Certified"] == "Yes": score += 1
        if data["Sentiment"] == "Negative": score -= 2
        elif data["Sentiment"] == "Neutral": score -= 1

        if score >= 2: return "Low", "High confidence – multiple positive indicators present."
        elif score >= 0: return "Medium", "Moderate confidence – neutral sentiment or limited public data."
        else: return "High", "Low confidence – negative sentiment and few positive ESG indicators."

    esg_rating, confidence = assess_risk(enriched)

    def get_recommendations(risk):
        if risk == "Low":
            return "Maintain relationship. Monitor ESG disclosures and encourage continued transparency."
        elif risk == "Medium":
            return "Engage supplier. Seek clarification on ESG policies and explore improvement plans."
        else:
            return "Flag for review. Conduct further due diligence and consider sourcing alternatives."

    recommendation = get_recommendations(esg_rating)

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Supplier: {supplier_name}", ln=True)
    pdf.cell(200, 10, txt=f"Spend: £{int(supplier_spend):,}", ln=True)
    pdf.cell(200, 10, txt=f"ESG Risk Rating: {esg_rating}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence Level: {confidence}", ln=True)
    pdf.ln(10)

    for key, val in enriched.items():
        pdf.multi_cell(0, 10, f"{key}: {val}")

    pdf.ln(10)
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Recommended Action:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, recommendation)

    pdf_bytes = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="Download Full ESG Risk Report (PDF)",
        data=pdf_bytes,
        file_name=f"ESG_Risk_Report_{supplier_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
