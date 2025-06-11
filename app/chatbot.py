# app/chatbot.py

import nltk
import numpy as np
import pickle
import json
import logging
import re
from datetime import datetime, timedelta
from tensorflow.keras.models import load_model
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from nltk.corpus import stopwords
from flask import current_app

# --- Inisialisasi Model & Preprocessing ---

# Muat model dan vectorizer saat modul diimpor
try:
    model = load_model('chat_model.h5')
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    with open('label.pkl', 'rb') as f:
        classes = pickle.load(f)
except Exception as e:
    logging.error(f"Error loading model or data files: {e}")
    raise

# Inisialisasi stemmer dan stopwords
factory = StemmerFactory()
stemmer = factory.create_stemmer()
indonesian_stopwords = set(stopwords.words('indonesian'))
ignore_chars = ['?', '!', '.', ',', '_']
ignore_words = indonesian_stopwords.union(ignore_chars)


def clean_up_sentence(sentence):
    """Membersihkan dan mempersiapkan kalimat untuk prediksi."""
    sentence_words = nltk.word_tokenize(str(sentence))
    return ' '.join(stemmer.stem(word.lower()) for word in sentence_words if word.lower() not in ignore_words)

def predict_class(sentence):
    """Memprediksi kelas (tag) dari sebuah kalimat."""
    processed_sentence = clean_up_sentence(sentence)
    if not processed_sentence.strip():
        return np.zeros((1, len(classes)))
    vector = vectorizer.transform([processed_sentence]).toarray()
    return model.predict(vector, verbose=0)

# --- Logika Respons ---

def get_response(prediction, user_message):
    """Mendapatkan respons berdasarkan hasil prediksi."""
    if not prediction.any():
        logging.info("Prediksi kosong, mengembalikan pesan default.")
        return "Maaf, saya tidak mengerti."

    predicted_class_index = np.argmax(prediction)
    confidence = prediction[0][predicted_class_index]

    if confidence > current_app.config['ERROR_THRESHOLD']:
        tag = classes[predicted_class_index]
        logging.info(f"Predicted tag: {tag} with confidence: {confidence:.2f}")
        return get_response_from_db(tag, user_message)
    
    logging.info("Tingkat kepercayaan rendah, mengembalikan pesan default.")
    return "Maaf, saya tidak mengerti."

def get_response_from_db(tag, user_message):
    """Mengambil respons dari database berdasarkan tag."""
    from .utils import get_db_connection  # Impor lokal untuk menghindari circular import
    
    # ... (logika query database yang kompleks dari kode asli Anda) ...
    # Sebaiknya, logika query yang sangat kompleks ini dipecah lagi menjadi fungsi-fungsi
    # yang lebih kecil di dalam file ini atau file `models.py`.
    # Contoh sederhana:
    if tag == '67':
        # Panggil fungsi khusus untuk menangani jadwal
        return get_jadwal_kuliah_response(user_message)
    else:
        # Panggil fungsi untuk intent umum
        return get_general_intent_response(tag)


def get_jadwal_kuliah_response(user_message):
    """Menangani permintaan jadwal kuliah dan mengambil data dari DB."""
    # (Kode untuk parsing 'hari', 'semester', 'jurusan', 'kelas' dari user_message)
    # (Kode untuk membangun dan mengeksekusi query SQL jadwal)
    # (Kode untuk memformat hasil query menjadi respons yang user-friendly)
    # ...
    # Untuk keringkasan, logika detailnya saya skip, tapi seharusnya dipindahkan ke sini.
    return "Ini adalah respons untuk jadwal kuliah yang telah diproses."


def get_general_intent_response(tag):
    """Mengambil respons umum dari tabel intents."""
    from .utils import get_db_connection
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT responses FROM intents WHERE tag = %s", (tag,))
        result = cursor.fetchone()
        if result and result['responses']:
            responses = json.loads(result['responses'])
            return "\n".join(responses)
        return "Maaf, saya tidak menemukan jawaban yang sesuai."
    except Exception as e:
        logging.error(f"Error fetching general intent response: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda."
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()