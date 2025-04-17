from pymongo import MongoClient
from bson import ObjectId
from app.config import Config

client = MongoClient(Config.MONGO_URI)
db = client.get_database('certificates_db')

class CertificateDB:
    @staticmethod
    def save_certificate(data):
        result = db.certificates.insert_one(data)
        return {
            '_id': str(result.inserted_id),  # Ensure string conversion
            **data
        }

    @staticmethod
    def get_certificates(filter={}):
        return [
            {**doc, '_id': str(doc['_id'])}  # Convert ObjectId in query results
            for doc in db.certificates.find(filter)
        ]