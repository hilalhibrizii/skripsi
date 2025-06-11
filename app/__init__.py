# app/__init__.py

import warnings
from flask import Flask
import nltk
from config import config

def create_app(config_class=config):
    """Membuat dan mengonfigurasi instance aplikasi Flask."""
    
    # Filter warnings
    warnings.filterwarnings("ignore")

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Download NLTK data jika belum ada
    _download_nltk_data()

    # Registrasi Blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
    
    return app

def _download_nltk_data():
    """Mengecek dan mengunduh data NLTK yang diperlukan."""
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)