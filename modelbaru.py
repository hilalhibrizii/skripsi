# Import necessary libraries
import warnings
warnings.filterwarnings("ignore")
import nltk
import pandas as pd
import pickle
import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.metrics import f1_score
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Initialize Indonesian stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Download NLTK data
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

# Configuration
ignore_chars = ['?', '!', '.', ',', '_']
indonesian_stopwords = set(stopwords.words('indonesian'))
ignore_words = indonesian_stopwords.union(ignore_chars)

# Load training and validation data
df_train = pd.read_csv("stikom_dataset.csv")
questions_train = df_train["pertanyaan"].tolist()
labels_train = df_train["label"].tolist()

df_val = pd.read_csv("stikom_validation_dataset.csv")
questions_val = df_val["pertanyaan"].tolist()
labels_val = df_val["label"].tolist()

# Preprocessing data
words = []
classes = []
documents_train = []
documents_val = []

for question, label in zip(questions_train, labels_train):
    word_tokens = nltk.word_tokenize(question)
    stemmed_words = [stemmer.stem(w.lower()) for w in word_tokens if w not in ignore_words]
    words.extend(stemmed_words)
    documents_train.append((stemmed_words, str(label)))
    if str(label) not in classes:
        classes.append(str(label))

for question, label in zip(questions_val, labels_val):
    word_tokens = nltk.word_tokenize(question)
    stemmed_words = [stemmer.stem(w.lower()) for w in word_tokens if w not in ignore_words]
    words.extend(stemmed_words)
    documents_val.append((stemmed_words, str(label)))

words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

pickle.dump(words, open('texts.pkl', 'wb'))
pickle.dump(classes, open('label.pkl', 'wb'))

training = []
validation = []
output_empty = [0] * len(classes)

for doc in documents_train:
    bag = []
    pattern_words = doc[0]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    training.append([bag, output_row])

for doc in documents_val:
    bag = []
    pattern_words = doc[0]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    validation.append([bag, output_row])

random.shuffle(training)
random.shuffle(validation)
training = np.array(training, dtype=object)
validation = np.array(validation, dtype=object)

X_train = np.array(list(training[:, 0]), dtype=np.float32)
y_train = np.array(list(training[:, 1]), dtype=np.float32)
X_val = np.array(list(validation[:, 0]), dtype=np.float32)
y_val = np.array(list(validation[:, 1]), dtype=np.float32)

# Build simpler model
model = Sequential()
model.add(Dense(128, input_shape=(len(X_train[0]),), activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(64, activation='relu'))
model.add(Dense(len(y_train[0]), activation='softmax'))

early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

model.compile(loss='categorical_crossentropy', optimizer=Adam(learning_rate=0.0005), metrics=['accuracy'])

history = model.fit(
    X_train, y_train,
    epochs=3000,
    batch_size=32,
    verbose=1,
    validation_data=(X_val, y_val),
    callbacks=[early_stop]
)

model.save('chat_model.h5')
print("\nModel berhasil dibuat dan disimpan!")

# Evaluate
y_val_pred = model.predict(X_val)
y_val_true = np.argmax(y_val, axis=1)
y_val_pred_classes = np.argmax(y_val_pred, axis=1)

f1_macro = f1_score(y_val_true, y_val_pred_classes, average='macro')
f1_weighted = f1_score(y_val_true, y_val_pred_classes, average='weighted')

print("\nEvaluasi Model pada Data Validasi:")
print(f"F1 Score (Macro): {f1_macro:.4f}")
print(f"F1 Score (Weighted): {f1_weighted:.4f}")
print(f"Accuracy (Validation): {history.history['val_accuracy'][-1]:.4f}")

tag_accuracy = {}
for tag in range(len(classes)):
    tag_indices = np.where(y_val_true == tag)[0]
    if len(tag_indices) > 0:
        correct = np.sum(y_val_pred_classes[tag_indices] == y_val_true[tag_indices])
        total = len(tag_indices)
        accuracy_percent = (correct / total) * 100
        tag_accuracy[tag] = accuracy_percent
    else:
        tag_accuracy[tag] = None

print("\nSkor Akurasi per Tag (Persen):")
for tag, acc in tag_accuracy.items():
    if acc is not None:
        print(f"Tag {tag}: {acc:.2f}% ({np.sum(y_val_true == tag)} sampel di validasi)")
    else:
        print(f"Tag {tag}: Tidak ada data di validasi")