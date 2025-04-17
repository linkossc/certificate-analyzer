from app import create_app
from app.config import Config
import os

if __name__ == '__main__':
    app = create_app()

    # Ensure upload directory exists
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)

    # Start the API
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Prevents duplicate processes
    )