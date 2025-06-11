# app/api.py

from flask import Blueprint, request, jsonify, current_app
from .utils import login_required, get_db_connection
import json
import logging

# Membuat Blueprint untuk API
api = Blueprint('api', __name__)

# ======================================================================
# API ENDPOINTS UNTUK INTENTS
# ======================================================================

@api.route('/intents', methods=['GET'])
@login_required
def get_intents():
    """Mengambil semua data intent dari database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT tag, patterns, responses FROM intents")
        results = cursor.fetchall()
        # Ubah string JSON menjadi list Python
        for result in results:
            result['patterns'] = json.loads(result['patterns']) if result['patterns'] else []
            result['responses'] = json.loads(result['responses']) if result['responses'] else []
        return jsonify(results)
    except Exception as e:
        logging.error(f"Error getting intents: {e}")
        return jsonify({"error": "Gagal mengambil data intents"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@api.route('/intents', methods=['POST'])
@login_required
def add_intent():
    """Menambahkan intent baru ke database."""
    data = request.get_json()
    tag = data.get('tag')
    patterns = data.get('patterns', [])
    responses = data.get('responses', [])

    if not tag:
        return jsonify({"error": "Tag wajib diisi"}), 400
    if not isinstance(patterns, list) or not isinstance(responses, list):
        return jsonify({"error": "Patterns dan responses harus dalam format list"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO intents (tag, patterns, responses) VALUES (%s, %s, %s)"
        cursor.execute(query, (tag, json.dumps(patterns), json.dumps(responses)))
        conn.commit()
        logging.info(f"Intent '{tag}' berhasil ditambahkan.")
        return jsonify({"message": "Intent berhasil ditambahkan"}), 201
    except Exception as e:
        logging.error(f"Database error saat menambah intent: {e}")
        return jsonify({"error": "Gagal menambahkan intent ke database"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@api.route('/intents/<string:tag>', methods=['PUT'])
@login_required
def update_intent(tag):
    """Memperbarui intent yang sudah ada berdasarkan tag."""
    data = request.get_json()
    patterns = data.get('patterns', [])
    responses = data.get('responses', [])

    if not isinstance(patterns, list) or not isinstance(responses, list):
        return jsonify({"error": "Patterns dan responses harus dalam format list"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "UPDATE intents SET patterns = %s, responses = %s WHERE tag = %s"
        cursor.execute(query, (json.dumps(patterns), json.dumps(responses), tag))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Tag tidak ditemukan"}), 404
        logging.info(f"Intent '{tag}' berhasil diperbarui.")
        return jsonify({"message": "Intent berhasil diperbarui"})
    except Exception as e:
        logging.error(f"Database error saat update intent: {e}")
        return jsonify({"error": "Gagal memperbarui intent"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

# ======================================================================
# API ENDPOINTS UNTUK JADWAL KULIAH
# ======================================================================

@api.route('/jadwal', methods=['GET'])
@login_required
def get_all_jadwal():
    """Mengambil semua jadwal kuliah dengan filter."""
    search_query = request.args.get('search', '').strip()
    semester_filter = request.args.get('semester', '').strip()
    semester_aktif = current_app.config['SEMESTER_AKTIF']
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        base_query = """
            SELECT id_jadwal, hari, semester, jurusan, kelas, mata_kuliah, 
                   TIME_FORMAT(jam_mulai, '%H:%i') as jam_mulai,
                   TIME_FORMAT(jam_selesai, '%H:%i') as jam_selesai,
                   dosen, ruangan, semester_type
            FROM jadwal_kuliah
            WHERE semester_type = %s
        """
        params = [semester_aktif]

        if semester_filter:
            base_query += " AND semester = %s"
            params.append(semester_filter)
        
        if search_query:
            base_query += """
                AND (LOWER(hari) LIKE %s OR LOWER(jurusan) LIKE %s OR LOWER(kelas) LIKE %s OR 
                     LOWER(mata_kuliah) LIKE %s OR LOWER(dosen) LIKE %s OR LOWER(ruangan) LIKE %s)
            """
            search_pattern = f"%{search_query.lower()}%"
            params.extend([search_pattern] * 6)

        base_query += " ORDER BY FIELD(hari, 'SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU', 'MINGGU'), jam_mulai"
        
        cursor.execute(base_query, tuple(params))
        jadwal = cursor.fetchall()
        return jsonify(jadwal)
    except Exception as e:
        logging.error(f"Error fetching all schedules: {e}")
        return jsonify({"error": "Gagal mengambil data jadwal"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@api.route('/jadwal/<int:id_jadwal>', methods=['GET'])
@login_required
def get_jadwal(id_jadwal):
    """Mengambil satu jadwal berdasarkan ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id_jadwal, hari, semester, jurusan, kelas, mata_kuliah,
                   TIME_FORMAT(jam_mulai, '%H:%i') as jam_mulai,
                   TIME_FORMAT(jam_selesai, '%H:%i') as jam_selesai,
                   dosen, ruangan, semester_type
            FROM jadwal_kuliah WHERE id_jadwal = %s
        """, (id_jadwal,))
        jadwal = cursor.fetchone()
        if not jadwal:
            return jsonify({"error": "Jadwal tidak ditemukan"}), 404
        return jsonify(jadwal)
    except Exception as e:
        logging.error(f"Error fetching schedule {id_jadwal}: {e}")
        return jsonify({"error": "Gagal mengambil data jadwal"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@api.route('/jadwal', methods=['POST'])
@login_required
def create_jadwal():
    """Membuat jadwal kuliah baru."""
    data = request.get_json()
    # Logika validasi dari file lama Anda
    required_fields = ['hari', 'semester', 'jurusan', 'kelas', 'mata_kuliah', 'jam_mulai', 'jam_selesai', 'dosen', 'ruangan']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Semua field wajib diisi"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO jadwal_kuliah 
            (hari, semester, jurusan, kelas, mata_kuliah, jam_mulai, jam_selesai, dosen, ruangan, semester_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            data['hari'], data['semester'], data['jurusan'], data['kelas'],
            data['mata_kuliah'], data['jam_mulai'], data['jam_selesai'],
            data['dosen'], data['ruangan'], current_app.config['SEMESTER_AKTIF']
        )
        cursor.execute(query, params)
        conn.commit()
        logging.info(f"Jadwal baru ditambahkan dengan ID: {cursor.lastrowid}")
        return jsonify({"message": "Jadwal berhasil ditambahkan!", "id": cursor.lastrowid}), 201
    except Exception as e:
        logging.error(f"Error creating schedule: {e}")
        return jsonify({"error": "Gagal menambahkan jadwal"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()


@api.route('/jadwal/<int:id_jadwal>', methods=['PUT'])
@login_required
def update_jadwal(id_jadwal):
    """Memperbarui jadwal kuliah berdasarkan ID."""
    data = request.get_json()
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            UPDATE jadwal_kuliah SET 
            hari = %s, semester = %s, jurusan = %s, kelas = %s, mata_kuliah = %s,
            jam_mulai = %s, jam_selesai = %s, dosen = %s, ruangan = %s, semester_type = %s
            WHERE id_jadwal = %s
        """
        params = (
            data.get('hari'), data.get('semester'), data.get('jurusan'), data.get('kelas'), 
            data.get('mata_kuliah'), data.get('jam_mulai'), data.get('jam_selesai'), 
            data.get('dosen'), data.get('ruangan'), 
            current_app.config['SEMESTER_AKTIF'], id_jadwal
        )
        cursor.execute(query, params)
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Jadwal tidak ditemukan"}), 404
        logging.info(f"Jadwal dengan ID {id_jadwal} berhasil diperbarui.")
        return jsonify({"message": "Jadwal berhasil diperbarui!"})
    except Exception as e:
        logging.error(f"Error updating schedule {id_jadwal}: {e}")
        return jsonify({"error": "Gagal memperbarui jadwal"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@api.route('/jadwal/<int:id_jadwal>', methods=['DELETE'])
@login_required
def delete_jadwal(id_jadwal):
    """Menghapus jadwal kuliah berdasarkan ID."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jadwal_kuliah WHERE id_jadwal = %s", (id_jadwal,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Jadwal tidak ditemukan"}), 404
        logging.info(f"Jadwal dengan ID {id_jadwal} berhasil dihapus.")
        return jsonify({"message": "Jadwal berhasil dihapus!"})
    except Exception as e:
        logging.error(f"Error deleting schedule {id_jadwal}: {e}")
        return jsonify({"error": "Gagal menghapus jadwal"}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()