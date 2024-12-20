from flask import Flask
from app.routes import routes
from dotenv import load_dotenv
import os

def create_app():
    # Load the environment variables from .env file
    load_dotenv()

    # Create the Flask app
    app = Flask(__name__, template_folder='app/template')

    # Set the secret key using an environment variable
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Register the routes blueprint
    app.register_blueprint(routes)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)