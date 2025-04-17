from flask import Flask
from flask.json.provider import DefaultJSONProvider  # New import
from bson import ObjectId
from flask_cors import CORS
from app.config import Config


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Set the custom JSON provider
    app.json_provider_class = CustomJSONProvider
    app.json = app.json_provider_class(app)  # Initialize provider

    # Validate configuration
    Config.validate()

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
