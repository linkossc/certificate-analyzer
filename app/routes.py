from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.utils import process_certificate, CertificateProcessingError
from services.database import CertificateDB
from app.config import Config
import os

main_bp = Blueprint('main', __name__)

@main_bp.route('/upload', methods=['POST'])
def handle_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({"error": "Invalid file"}), 400

    try:
        filename = secure_filename(file.filename)
        temp_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)

        # Process and save certificate
        certificate_data = process_certificate(temp_path)
        saved_data = CertificateDB.save_certificate(certificate_data)

        return jsonify({
            "message": "Certificate processed successfully",
            "data": saved_data  # Includes stringified _id
        }), 201

    except CertificateProcessingError as e:
        return jsonify({
            "error": str(e),
            "stage": e.stage,
            "details": str(e.original_error) if e.original_error else None
        }), 400

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)