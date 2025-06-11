# config.py

import os

class Config:
    """Konfigurasi dasar untuk aplikasi Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'stikom22j-is-a-strong-secret-key')
    DEBUG = False
    TESTING = False
    
    # Konfigurasi Database
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = ''
    DB_NAME = 'stikom_db'
    
    # Pengaturan Aplikasi
    SEMESTER_AKTIF = 'ganjil' # Bisa diubah melalui endpoint
    ERROR_THRESHOLD = 0.35

class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan development."""
    DEBUG = True

class ProductionConfig(Config):
    """Konfigurasi untuk lingkungan produksi."""
    pass

# Pilih konfigurasi yang akan digunakan
# Untuk development, gunakan DevelopmentConfig
config = DevelopmentConfig