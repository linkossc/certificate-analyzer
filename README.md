# Certificate Analyzer API

**AI-powered certificate data extraction** using Google Gemini and Flask.  
Extracts owner name, organization, skills, and dates from PDF certificates.

## Features
- PDF/OCR Support
- AI-Powered Analysis (Google Gemini)
- MongoDB Integration
- REST API Endpoints
- Date Parsing

## Technologies
- Flask (API framework)
- Google Gemini (NLP/ML)
- PyPDF2 + Tesseract OCR (PDF/text extraction)
- MongoDB (data storage)
- OpenCV (image preprocessing)

## Setup
```bash
git clone https://github.com/your-username/certificate-analyzer.git
cd certificate-analyzer
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY and TESSERACT_PATH in .env
python run.py
