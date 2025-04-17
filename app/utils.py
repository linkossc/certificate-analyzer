import re
import pytesseract
from datetime import datetime
from dateutil.parser import parse as parse_date
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Optional
import cv2
import numpy as np
from PIL import Image

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Google Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    logger.error("Google API key is missing. Please set GOOGLE_API_KEY in .env.")
    raise ValueError("Google API key is missing.")

genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')


class CertificateProcessingError(Exception):
    def __init__(self, message: str, stage: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.stage = stage
        self.original_error = original_error


def extract_text(pdf_path: str) -> str:
    """Enhanced text extraction with preprocessing"""
    try:
        # Direct text extraction
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            direct_text = "\n".join([page.extract_text() or "" for page in reader.pages])

        # OCR with image enhancement
        images = convert_from_path(pdf_path, dpi=300)
        ocr_text = []
        for img in images:
            # Convert to numpy array
            img = np.array(img)
            # Apply preprocessing
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            # Extract text
            ocr_text.append(pytesseract.image_to_string(thresh))

        # Combine results
        combined_text = "\n".join([direct_text.strip(), *ocr_text])
        cleaned_text = re.sub(r'[\x0c]+', '', combined_text).strip()

        logger.info(f"Extracted text:\n{cleaned_text}")
        return cleaned_text

    except Exception as e:
        raise CertificateProcessingError(
            f"Text extraction failed: {str(e)}",
            stage="text_extraction"
        )


def extract_organization(text: str) -> str:
    """Extract clean organization name"""
    try:
        prompt = f"""
        Extract ONLY the issuing organization's full official name from this certificate.
        Return just the name without any explanations, formatting, or extra text.
        Example: "Certiprof, LLC" or "Amazon Web Services"

        Certificate text:
        {text}
        """

        response = gemini_model.generate_content(prompt)
        organization = response.text.strip()

        # Cleanup
        organization = re.sub(r'[^\w\s,]', '', organization).strip()
        return organization if organization else "Unknown"
    except Exception as e:
        logger.error(f"Organization extraction error: {str(e)}")
        return "Unknown"


def extract_skills_gemini(text: str, organization: str) -> list:
    """Extract clean skill list"""
    try:
        prompt = f"""
        Extract ONLY a comma-separated list of technical skills from this certificate.
        Include both explicit and inferred skills. Avoid explanations or formatting.
        Example: "Scrum Framework, Agile Methodology, Sprint Planning"

        Certificate text:
        {text}
        """

        response = gemini_model.generate_content(prompt)
        skills = response.text.split(",")

        # Cleanup
        cleaned_skills = []
        for skill in skills:
            cleaned = re.sub(r'[\*\:\-\d\n].*', '', skill).strip()
            if cleaned and len(cleaned) > 3:
                cleaned_skills.append(cleaned)

        return cleaned_skills if cleaned_skills else ["General Certification Skills"]
    except Exception as e:
        logger.error(f"Skills extraction error: {str(e)}")
        return []


def process_certificate(pdf_path: str) -> Dict:
    """Process certificate and return structured data"""
    try:
        text = extract_text(pdf_path)
        lines = text.split('\n')

        # Parse basic info
        owner_name = lines[0].strip() if lines else "Unnamed Owner"
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)? [A-Za-z]+ \d{4})"
        date_matches = re.findall(date_pattern, text)

        certification_date = parse_date(date_matches[0]) if date_matches else None
        expiry_date = parse_date(date_matches[1]) if len(date_matches) > 1 else None

        # Extract organization and skills
        organization = extract_organization(text)
        skills = extract_skills_gemini(text, organization)

        # Validate
        if not owner_name or not certification_date:
            raise CertificateProcessingError(
                "Missing required fields: owner name or date",
                stage="validation"
            )

        return {
            'owner_name': owner_name,
            'date': certification_date.strftime('%Y-%m-%d'),
            'expiry_date': expiry_date.strftime('%Y-%m-%d') if expiry_date else None,
            'organization': organization,
            'skills': skills
        }

    except CertificateProcessingError:
        raise
    except Exception as e:
        raise CertificateProcessingError(
            f"Unexpected processing error: {str(e)}",
            stage="general_processing"
        )