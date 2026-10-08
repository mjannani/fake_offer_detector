
# AI-Based Fake Internship & Job Offer Detector

A Streamlit MVP for detecting suspicious internship/job offers.

## Features

- Analyse WhatsApp/LinkedIn/email/offer-letter text pasted by the user
- Risk score from 0-100
- LOW RISK / SUSPICIOUS / HIGH RISK result
- Detects:
  - registration/payment/activation fees
  - urgency and pressure
  - unrealistic guarantees
  - OTP/PIN/password/bank requests
  - suspicious communication channels
- Extracts:
  - company name
  - recruiter/HR
  - email
  - phone number
  - URLs
  - money mentioned
- Basic website DNS check
- Downloadable analysis report

## Windows Run Steps

1. Install Python 3.11 or newer.
2. Open Command Prompt inside this folder.
3. Create virtual environment:

```bash
python -m venv venv
```

4. Activate it:

```bash
venv\Scripts\activate
```

5. Install packages:

```bash
pip install -r requirements.txt
```

6. Run:

```bash
streamlit run app.py
```

7. Browser will open automatically. If not, open:

http://localhost:8501

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py` and `requirements.txt`.
3. Open Streamlit Community Cloud.
4. Select the GitHub repository.
5. Set main file to `app.py`.
6. Deploy.

## Important limitation

This version does NOT automatically read WhatsApp, LinkedIn or phone calls. A normal Streamlit web app cannot silently access other apps or phone calls.

For the final product, use:

- Android app for caller/notification/share integration
- Browser extension for LinkedIn/WhatsApp Web/Gmail
- Streamlit or FastAPI backend for analysis
- Database for verified companies/recruiters
- Optional external verification APIs
- OCR for offer letters/screenshots

The current version is designed as a working college-project MVP and can be extended into the full product.
