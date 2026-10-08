
import re
import socket
from urllib.parse import urlparse

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Fake Internship & Job Offer Detector",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI-Based Fake Internship & Job Offer Detector")
st.caption("Analyse internship, job, recruiter and offer messages without interrupting your call or chat.")

SUSPICIOUS_PATTERNS = {
    "Payment / registration fee": [
        r"\bregistration fee\b", r"\bprocessing fee\b", r"\bsecurity deposit\b",
        r"\bactivation fee\b", r"\btraining fee\b", r"\bpay\s*(rs\.?|₹)?\s*\d+",
        r"\bpay\s*now\b", r"\bpayment\b"
    ],
    "Urgency / pressure": [
        r"\burgent\b", r"\bimmediately\b", r"\btoday only\b", r"\blast chance\b",
        r"\bwithin \d+ (hours?|minutes?)\b", r"\bdo not miss\b"
    ],
    "Unrealistic offer": [
        r"\b100% guaranteed\b", r"\bguaranteed job\b", r"\bno interview\b",
        r"\bwork from home\b.{0,80}\b\d{2,3},?\d{3,}\b",
        r"\bearn\b.{0,30}\b\d{2,3},?\d{3,}\b"
    ],
    "Sensitive information request": [
        r"\botp\b", r"\bupi pin\b", r"\bpin\b", r"\bpassword\b",
        r"\bbank account\b", r"\bcredit card\b", r"\bdebit card\b"
    ],
    "Suspicious communication": [
        r"\btelegram\b", r"\bwhatsapp only\b", r"\bgmail\.com\b",
        r"\byahoo\.com\b", r"\boutlook\.com\b"
    ]
}

def extract_email(text):
    return re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)

def extract_phone(text):
    return re.findall(r'(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)', text)

def extract_urls(text):
    return re.findall(r'https?://[^\s<>"\']+', text)

def extract_money(text):
    return re.findall(r'(?:₹|rs\.?|inr)\s?[\d,]+', text, flags=re.I)

def extract_company(text):
    patterns = [
        r'(?:company|organization|organisation)\s*(?:name)?\s*[:\-]\s*([A-Za-z0-9&.,()\- ]{2,80})',
        r'(?:at|from|with)\s+([A-Z][A-Za-z0-9&.,()\- ]{2,60})'
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.I)
        if m:
            value = m.group(1).strip(" .,:;-")
            if len(value) > 2:
                return value
    return "Not clearly detected"

def extract_recruiter(text):
    patterns = [
        r'(?:recruiter|hr|hiring manager|contact person)\s*(?:name)?\s*[:\-]\s*([A-Za-z][A-Za-z .]{2,50})'
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.I)
        if m:
            return m.group(1).strip()
    return "Not clearly detected"

def analyse_message(text):
    lower = text.lower()
    findings = []
    matched_categories = set()

    for category, patterns in SUSPICIOUS_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if re.search(pattern, lower, flags=re.I | re.S):
                matches.append(pattern)
        if matches:
            matched_categories.add(category)
            findings.append(category)

    score = min(100, len(findings) * 16)
    if extract_money(text):
        score = min(100, score + 10)
    if extract_email(text):
        score += 0
    if len(text) < 80:
        score = min(100, score + 5)

    if score >= 65:
        level = "HIGH RISK"
        emoji = "🔴"
        advice = "Do not pay money or share OTP, passwords, bank details or identity documents until independently verified."
    elif score >= 35:
        level = "SUSPICIOUS"
        emoji = "🟠"
        advice = "Verify the company, recruiter and official careers page before proceeding."
    else:
        level = "LOW RISK"
        emoji = "🟢"
        advice = "No major scam indicators were detected, but this is not a guarantee that the offer is genuine."

    return {
        "score": min(score, 100),
        "level": level,
        "emoji": emoji,
        "findings": findings,
        "advice": advice
    }

def check_website(url):
    try:
        parsed = urlparse(url)
        host = parsed.netloc or parsed.path
        host = host.split(":")[0]
        socket.gethostbyname(host)
        return {"status": "Reachable DNS", "host": host}
    except Exception:
        return {"status": "Could not verify DNS", "host": url}

with st.sidebar:
    st.header("⚙️ Analysis Mode")
    st.info(
        "Paste a recruiter message, email, LinkedIn message, WhatsApp text, "
        "or offer-letter text. The app analyses it locally using rule-based NLP."
    )
    st.warning("This MVP does not automatically read WhatsApp/LinkedIn/phone calls. Those integrations require platform/OS permissions.")

tab1, tab2, tab3 = st.tabs(["🔍 Analyse Message", "🏢 Company Details", "📊 Report"])

with tab1:
    st.subheader("Paste the message / offer details")

    sample = """Company Name: ABC Technologies
Recruiter: Rahul Kumar
Congratulations! You are selected for Data Analyst Internship.
Stipend: ₹25,000 per month.
Please pay ₹999 registration fee today to activate your internship.
Contact HR on WhatsApp: +91 9876543210
Email: hr.abctechnologies@gmail.com
Website: https://example.com
"""

    text = st.text_area(
        "Message / email / offer letter text",
        value="",
        height=260,
        placeholder="Paste the complete message here..."
    )

    c1, c2 = st.columns(2)
    with c1:
        analyse = st.button("🛡️ Analyse Now", type="primary", use_container_width=True)
    with c2:
        demo = st.button("🧪 Load Demo Message", use_container_width=True)

    if demo:
        text = sample
        st.session_state["analysis_text"] = sample
        st.rerun()

    if text:
        st.session_state["analysis_text"] = text

    active_text = st.session_state.get("analysis_text", text)

    if analyse or active_text:
        result = analyse_message(active_text)

        st.divider()
        a, b, c = st.columns(3)
        a.metric("Risk Score", f"{result['score']} / 100")
        b.metric("Risk Level", result["level"])
        c.metric("Detected Red Flags", len(result["findings"]))

        if result["score"] >= 65:
            st.error(f"{result['emoji']} {result['level']}")
        elif result["score"] >= 35:
            st.warning(f"{result['emoji']} {result['level']}")
        else:
            st.success(f"{result['emoji']} {result['level']}")

        st.progress(result["score"] / 100)

        if result["findings"]:
            st.subheader("🚩 Why was it flagged?")
            for item in result["findings"]:
                st.write(f"• **{item}**")
        else:
            st.success("No major scam patterns were detected.")

        st.info(f"💡 **Recommendation:** {result['advice']}")

        emails = extract_email(active_text)
        phones = extract_phone(active_text)
        urls = extract_urls(active_text)
        money = extract_money(active_text)

        st.subheader("📋 Extracted Information")
        info = {
            "Company": extract_company(active_text),
            "Recruiter / HR": extract_recruiter(active_text),
            "Emails": ", ".join(emails) if emails else "Not found",
            "Phone numbers": ", ".join(phones) if phones else "Not found",
            "Money mentioned": ", ".join(money) if money else "None detected",
            "URLs": ", ".join(urls) if urls else "Not found"
        }
        st.dataframe(pd.DataFrame(info.items(), columns=["Field", "Value"]), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("🏢 Company / Website Verification")
    company = st.text_input("Company name", placeholder="Example: ABC Technologies")
    website = st.text_input("Official website URL", placeholder="https://company.com")

    if st.button("🔎 Check Company Details", use_container_width=True):
        if company:
            st.write(f"### {company}")
            st.write("**Company name:**", company)
            st.write("**Website supplied:**", website if website else "Not supplied")
            st.write("**Careers page:**", f"{website.rstrip('/')}/careers" if website else "Not available")
            st.write("**Verification status:**")
            st.warning(
                "This MVP cannot guarantee legal/company registration verification. "
                "Use the official company website, LinkedIn company page and government/company registry for independent verification."
            )

        if website:
            check = check_website(website)
            st.write("**Website technical check:**", check["status"])
            st.write("**Detected host:**", check["host"])

with tab3:
    st.subheader("📊 Downloadable Analysis Report")

    report_text = st.session_state.get("analysis_text", "")
    if report_text:
        result = analyse_message(report_text)
        report = f"""AI-BASED FAKE INTERNSHIP & JOB OFFER DETECTOR
================================================

Risk Score: {result['score']}/100
Risk Level: {result['level']}

Company: {extract_company(report_text)}
Recruiter/HR: {extract_recruiter(report_text)}
Emails: {", ".join(extract_email(report_text)) or "Not found"}
Phone Numbers: {", ".join(extract_phone(report_text)) or "Not found"}
URLs: {", ".join(extract_urls(report_text)) or "Not found"}

RED FLAGS
---------
"""
        report += "\n".join(f"- {x}" for x in result["findings"]) or "- No major indicators detected"
        report += f"\n\nRECOMMENDATION\n--------------\n{result['advice']}\n"
        st.text_area("Report preview", report, height=350)
        st.download_button(
            "⬇️ Download TXT Report",
            data=report,
            file_name="fake_job_offer_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Analyse a message first to generate a report.")

st.divider()
st.caption("⚠️ This is a screening tool, not a legal or cybersecurity guarantee. Always verify important offers through official channels.")
