
import streamlit as st
import pandas as pd
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import datetime

st.set_page_config(page_title="Full ESG Risk Assessment Tool", layout="wide")

st.title("ESG Risk Assessment Tool")
st.markdown("Enter a supplier name and spend to generate a full ESG risk profile and report.")

supplier_name = st.text_input("Supplier Name")
supplier_spend = st.number_input("Spend (£)", min_value=0, step=1000)

if st.button("Run Full ESG Assessment") and supplier_name:
    enriched = {}

    def check_sbti(name):
        try:
            r = requests.get("https://sciencebasedtargets.org/companies-taking-action", timeout=10)
            return "Yes" if name.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def check_bcorp(name):
        try:
            r = requests.get(f"https://www.bcorporation.net/en-us/find-a-b-corp/?search={name}", timeout=10)
            return "Yes" if name.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def check_llw(name):
        try:
            r = requests.get("https://www.livingwage.org.uk/accredited-living-wage-employers", timeout=10)
            return "Yes" if name.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def check_fair_payment_code(name):
        try:
            r = requests.get("https://www.smallbusinesscommissioner.gov.uk/fair-payment", timeout=10)
            return "Yes" if name.lower() in r.text.lower() else "No"
        except:
            return "Unknown"

    def get_sentiment(name):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://www.bing.com/news/search?q={name}", headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            headlines = [a.get_text() for a in soup.find_all("a") if a.get_text()]
            sample = "; ".join(headlines[:3])
            score = TextBlob(" ".join(headlines)).sentiment.polarity
            sentiment = "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral"
            return sentiment, sample
        except:
            return "Unknown", "N/A"

    def estimate_category(name):
        return "Logistics" if "transport" in name.lower() or "logistic" in name.lower() else "Professional Services"

    def emissions_by_category(category, spend):
        try:
            factor = {
                "Logistics": 0.21,
                "Professional Services": 0.04,
                "Textiles": 0.31,
                "Construction": 0.18
            }.get(category, 0.05)
            return round(factor * (spend / 1000), 2)
        except:
            return "Unknown"

    enriched["SBTi Aligned"] = check_sbti(supplier_name)
    enriched["B Corp Certified"] = check_bcorp(supplier_name)
    enriched["LLW Accredited"] = check_llw(supplier_name)
    enriched["Fair Payment Code Signatory"] = check_fair_payment_code(supplier_name)
    enriched["Sentiment"], enriched["Media Example"] = get_sentiment(supplier_name)
    enriched["Carbon Conversion Category"] = estimate_category(supplier_name)
    enriched["Estimated Emissions (tCO2e)"] = emissions_by_category(enriched["Carbon Conversion Category"], supplier_spend)

    enriched.update({
        "Scope 1 & 2 Emissions (tCO2e)": enriched["Estimated Emissions (tCO2e)"],
        "Supplier Diversity": "Unknown",
        "Board Diversity": "Unknown",
        "Ownership Structure": "Unknown",
        "Modern Slavery Statement": "Unknown",
        "Factory Conditions Reported": "Unknown",
        "Whistleblowing Cases": "Unknown",
        "Sedex Member": "Unknown",
        "3rd Party Manufacturing": "Unknown"
    })

    # Risk Scoring
    def calculate_score(data):
        score = 0
        if data["SBTi Aligned"] == "Yes": score += 2
        if data["B Corp Certified"] == "Yes": score += 2
        if data["LLW Accredited"] == "Yes": score += 1
        if data["Fair Payment Code Signatory"] == "Yes": score += 1
        if data["Sentiment"] == "Negative": score -= 2
        elif data["Sentiment"] == "Neutral": score -= 1
        return score

    score = calculate_score(enriched)
    rating = "Low" if score >= 4 else "Medium" if score >= 1 else "High"
    confidence = "High" if score >= 4 else "Moderate" if score >= 1 else "Low"
    recommendation = {
        "Low": "Maintain relationship and encourage ongoing ESG disclosure.",
        "Medium": "Engage supplier and explore improvement opportunities.",
        "High": "Conduct further due diligence and consider alternatives."
    }[rating]

    # PDF Build
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="ESG Risk Assessment Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Date: {datetime.date.today()}", ln=True)
    pdf.cell(200, 10, txt=f"Supplier: {supplier_name}", ln=True)
    pdf.cell(200, 10, txt=f"Spend: £{int(supplier_spend):,}", ln=True)
    pdf.cell(200, 10, txt=f"ESG Risk Rating: {rating}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence Level: {confidence}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Environmental", ln=True)
    pdf.set_font("Arial", size=12)
    for key in ["SBTi Aligned", "B Corp Certified", "LLW Accredited", "Carbon Conversion Category", "Scope 1 & 2 Emissions (tCO2e)", "Estimated Emissions (tCO2e)"]:
        pdf.cell(200, 10, txt=f"{key}: {enriched[key]}", ln=True)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Social", ln=True)
    pdf.set_font("Arial", size=12)
    for key in ["Supplier Diversity", "Board Diversity", "Modern Slavery Statement", "Factory Conditions Reported", "Whistleblowing Cases"]:
        pdf.cell(200, 10, txt=f"{key}: {enriched[key]}", ln=True)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Governance", ln=True)
    pdf.set_font("Arial", size=12)
    for key in ["Ownership Structure", "Fair Payment Code Signatory", "Sedex Member", "3rd Party Manufacturing"]:
        pdf.cell(200, 10, txt=f"{key}: {enriched[key]}", ln=True)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Media Sentiment", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Sentiment: {enriched['Sentiment']}", ln=True)
    pdf.multi_cell(0, 10, f"Example: {enriched['Media Example']}")
    pdf.ln(5)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt="Recommendations", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, recommendation)

    pdf_bytes = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="Download Full ESG Risk Report (PDF)",
        data=pdf_bytes,
        file_name=f"ESG_Risk_Report_{supplier_name.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
