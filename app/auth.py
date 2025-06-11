# app/auth.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
import logging
from .utils import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Menangani proses login admin."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password') # Catatan: Password harusnya di-hash!

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            
            if user:
                session['logged_in'] = True
                session['username'] = user['username']
                logging.info(f"Pengguna {user['username']} berhasil login.")
                return redirect(url_for('main.admin'))
            else:
                return render_template('login.html', error="Username atau password salah.")

        except Exception as e:
            logging.error(f"Error saat login: {e}")
            return render_template('login.html', error="Terjadi kesalahan pada server.")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    return render_template('login.html')

@auth.route('/logout')
def logout():
    """Menghapus sesi pengguna (logout)."""
    session.clear()
    logging.info("Pengguna berhasil logout.")
    return redirect(url_for('auth.login'))