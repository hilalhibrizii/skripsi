# app/utils.py

import mysql.connector
import logging
from functools import wraps
from flask import session, redirect, url_for, current_app

def get_db_connection():
    """Membuka koneksi baru ke database MySQL."""
    try:
        connection = mysql.connector.connect(
            host=current_app.config['DB_HOST'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            database=current_app.config['DB_NAME']
        )
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        raise

# PASTIKAN FUNGSI INI ADA DAN NAMANYA SUDAH BENAR
def login_required(f):
    """Decorator untuk memastikan pengguna sudah login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            logging.warning("Akses tidak sah, pengguna akan diarahkan ke halaman login.")
            # Perhatikan perubahan di sini untuk mencocokkan blueprint
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function