import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf').split(','))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    MONGO_URI = os.getenv('MONGO_URI')
    TESSERACT_PATH = os.getenv('TESSERACT_PATH')
    SKILL_KEYWORDS = {
        'en': ['skills?', 'expertise in', 'certified in'],
        'fr': ['compétences', 'expertise en', 'certifié en']
    }

    @staticmethod
    def validate():
        if not Config.MONGO_URI:
            raise ValueError("MONGO_URI is not set in .env")
        if not Config.TESSERACT_PATH or not os.path.exists(Config.TESSERACT_PATH):
            raise ValueError("TESSERACT_PATH is invalid or missing")