from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import nltk
import numpy as np
import pickle
from tensorflow.keras.models import load_model
import mysql.connector
import json
import logging
from functools import wraps
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Inisialisasi aplikasi Flask
app = Flask(__name__)

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)

# Secret key untuk session
app.secret_key = 'stikom22j'

# Inisialisasi stemmer Sastrawi
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Memuat model dan data
model = load_model('chat_model.h5')
with open('texts.pkl', 'rb') as f:
    words = pickle.load(f)
with open('label.pkl', 'rb') as f:
    classes = pickle.load(f)

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

# Konfigurasi stopwords
indonesian_stopwords = set(stopwords.words('indonesian'))
ignore_chars = ['?', '!', '.', ',', '_']
ignore_words = indonesian_stopwords.union(ignore_chars)

# Konfigurasi database MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'stikom_db'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Database connection error: {err}")
        raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            logging.warning("User not logged in, redirecting to login")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM admin WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            if user:
                session['logged_in'] = True
                session['username'] = user['username']
                logging.info(f"Session created for user: {session['username']}")
                return redirect(url_for('admin'))
            else:
                return render_template('login.html', error="Invalid username or password")
        except mysql.connector.Error as err:
            logging.error(f"Database error: {err}")
            return render_template('login.html', error="Something went wrong")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
@login_required
def admin():
    logging.info("Admin page accessed by user: %s", session.get('username'))
    return render_template('admin.html')

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [stemmer.stem(word.lower()) for word in sentence_words if word.lower() not in ignore_words]

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for word in sentence_words:
        for i, w in enumerate(words):
            if w == word:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    p = bow(sentence, words)
    prediction = model.predict(np.array([p]), verbose=0)
    return prediction

def get_response_from_db(tag):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT responses FROM intents WHERE tag = %s"
        cursor.execute(query, (tag,))
        result = cursor.fetchone()
        if result:
            responses = json.loads(result[0])
            if isinstance(responses, list):
                return "\n".join(responses)
            else:
                logging.error("Invalid responses format in database")
                return "maaf saya tidak mengerti."
        else:
            return "maaf saya tidak mengerti."
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return "maaf, terjadi kesalahan."
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_response(prediction):
    ERROR_THRESHOLD = 0.49
    predicted_class = np.argmax(prediction)
    if prediction[0][predicted_class] > ERROR_THRESHOLD:
        tag = classes[predicted_class]
        return get_response_from_db(tag)
    return "Maaf, Saya tidak mengerti"

@app.route('/get_response', methods=['POST'])
def chatbot_response():
    user_message = request.form.get('message')
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    logging.info(f"User message: {user_message}")
    prediction = predict_class(user_message)
    response = get_response(prediction)
    logging.info(f"Bot response: {response}")
    return jsonify({'response': response})

@app.route('/intents', methods=['GET'])
@login_required
def get_intents():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT tag, patterns, responses FROM intents"
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            result['patterns'] = json.loads(result['patterns']) if result['patterns'] else []
            result['responses'] = json.loads(result['responses']) if result['responses'] else []
        return jsonify(results)
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/intents', methods=['POST'])
@login_required
def add_intent():
    data = request.get_json()
    tag = data.get('tag')
    patterns = data.get('patterns', [])
    responses = data.get('responses', [])
    if not tag:
        return jsonify({"error": "Tag is required"}), 400
    if not isinstance(patterns, list) or not isinstance(responses, list):
        return jsonify({"error": "Patterns and responses must be lists"}), 400
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO intents (tag, patterns, responses) VALUES (%s, %s, %s)"
        cursor.execute(query, (tag, json.dumps(patterns), json.dumps(responses)))
        connection.commit()
        return jsonify({"message": "Intent added successfully"}), 201
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/intents/<tag>', methods=['PUT'])
@login_required
def update_intent(tag):
    data = request.get_json()
    patterns = data.get('patterns', [])
    responses = data.get('responses', [])
    if not isinstance(patterns, list) or not isinstance(responses, list):
        return jsonify({"error": "Patterns and responses must be lists"}), 400
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "UPDATE intents SET patterns = %s, responses = %s WHERE tag = %s"
        cursor.execute(query, (json.dumps(patterns), json.dumps(responses), tag))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Tag not found"}), 404
        return jsonify({"message": "Intent updated successfully"})
    except mysql.connector.Error as err:
        logging.error(f"Database error: {err}")
        return jsonify({"error": "Something went wrong"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)