from flask import Flask
from config import Config
from extensions import jwt
from login.routes import login_bp
from messages.routes import messages_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize JWT
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(login_bp, url_prefix="/auth")
    app.register_blueprint(messages_bp, url_prefix="/messages")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
