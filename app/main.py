# app/main.py

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from .utils import login_required
from .chatbot import predict_class, get_response
from .models import Intent, JadwalKuliah

main = Blueprint('main', __name__)

# --- Rute Halaman ---

@main.route('/')
def index():
    """Menampilkan halaman utama chatbot."""
    return render_template('index.html')

@main.route('/admin')
@login_required
def admin():
    """Menampilkan dashboard admin untuk mengelola intent."""
    return render_template('admin.html', username=session.get('username'))

@main.route('/jadwal-kuliah')
@login_required
def jadwal_kuliah_page():
    """Menampilkan halaman manajemen jadwal kuliah."""
    return render_template('jadwal.html')

# --- API Endpoint untuk Chatbot ---

@main.route('/get_response', methods=['POST'])
def chatbot_response():
    """Endpoint untuk menerima pesan pengguna dan memberikan respons chatbot."""
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    prediction = predict_class(user_message)
    response = get_response(prediction, user_message)
    
    return jsonify({'response': response})

# --- API Endpoint untuk Konfigurasi Semester ---

@main.route('/set-semester', methods=['POST'])
@login_required
def set_semester():
    data = request.get_json()
    semester = data.get('semester_type')
    if semester in ['ganjil', 'genap']:
        current_app.config['SEMESTER_AKTIF'] = semester
        return jsonify({"message": f"Semester aktif berhasil diatur ke {semester}"})
    return jsonify({"error": "Jenis semester tidak valid"}), 400

@main.route('/get-semester', methods=['GET'])
def get_semester():
    return jsonify({"semester_type": current_app.config.get('SEMESTER_AKTIF', 'ganjil')})

# --- API untuk CRUD Intents ---
# (Rute /intents GET, POST, PUT dipindahkan ke sini, menggunakan kelas Intent dari models.py)

# --- API untuk CRUD Jadwal ---
# (Rute /jadwal GET, POST, PUT, DELETE dipindahkan ke sini, menggunakan kelas JadwalKuliah dari models.py)