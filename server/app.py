from flask import Flask
from config import Config
from extensions import jwt, init_mongo
from login import login_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extensions
    jwt.init_app(app)
    init_mongo(app)

    # Blueprints
    app.register_blueprint(login_bp, url_prefix="/auth")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
