import sqlite3
from cryptography.fernet import Fernet
import os
from datetime import datetime

# Save the encryption key to a file
def save_key(key):
    with open('secret.key', 'wb') as key_file:
        key_file.write(key)

# Load the encryption key from a file
def load_key():
    with open('secret.key', 'rb') as key_file:
        return key_file.read()

# Generate or load encryption key
if not os.path.exists('secret.key'):
    encryption_key = Fernet.generate_key()
    save_key(encryption_key)
else:
    encryption_key = load_key()

# Global cipher object
cipher = Fernet(encryption_key)

def get_cipher():
    return cipher

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        message BLOB,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS file_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        receiver TEXT,
        filename BLOB,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS voice_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    filename BLOB,
    timestamp TEXT
    )''')

    conn.commit()
    conn.close()
# Log messages in the SQLite database (with encryption) - sender side only
def log_message(sender, receiver, message):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    encrypted_message = cipher.encrypt(message.encode('utf-8'))  # Store as binary
    c.execute('INSERT INTO chat_log (sender, receiver, message, timestamp) VALUES (?, ?, ?, ?)', 
              (sender, receiver, encrypted_message, timestamp))
    conn.commit()
    conn.close()

# Log files in the SQLite database (with encryption) - sender side only
def log_file(sender, receiver, filename):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    encrypted_filename = cipher.encrypt(filename.encode('utf-8'))  # Store as binary
    c.execute('INSERT INTO file_log (sender, receiver, filename, timestamp) VALUES (?, ?, ?, ?)', 
              (sender, receiver, encrypted_filename, timestamp))
    conn.commit()
    conn.close()
def log_voice(sender, receiver, filename):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    encrypted_filename = cipher.encrypt(filename.encode('utf-8'))
    c.execute('INSERT INTO voice_log (sender, receiver, filename, timestamp) VALUES (?, ?, ?, ?)', 
              (sender, receiver, encrypted_filename, timestamp))
    conn.commit()
    conn.close()


# Retrieve previous chat logs (decryption done here)
def load_previous_chat(sender, receiver):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    
    # Fetch chat history for the sender-receiver pair
    c.execute('SELECT sender, message, timestamp FROM chat_log WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)', 
              (sender, receiver, receiver, sender))
    chat_history = c.fetchall()
    conn.close()
    
    decrypted_history = []
    
    for msg_sender, encrypted_message, ts in chat_history:
        try:
            # Decrypt the message
            decrypted_msg = cipher.decrypt(encrypted_message).decode('utf-8')
            decrypted_history.append((msg_sender, decrypted_msg, ts))
        except Exception as e:
            print(f"Decryption failed for message: {encrypted_message}. Error: {e}")
            decrypted_history.append((msg_sender, "[Decryption Failed]", ts))  # Indicate failure in chat history

    return decrypted_history

# Retrieve previous file logs (decryption done here)
def load_previous_files(sender, receiver):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT sender, filename, timestamp FROM file_log WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)', 
              (sender, receiver, receiver, sender))
    file_history = c.fetchall()
    conn.close()
    
    decrypted_files = []
    
    for file_sender, encrypted_filename, ts in file_history:
        try:
            # Attempt to decrypt the filename
            decrypted_fname = cipher.decrypt(encrypted_filename).decode('utf-8')
        except Exception as e:
            print(f"Decryption failed for file: {encrypted_filename}. Error: {e}")
            decrypted_fname = "[Decryption Failed]"  # Indicate failure for the filename

        decrypted_files.append((file_sender, decrypted_fname, ts))
    
    return decrypted_files
# Retrieve previous voice messages (decryption done here)
def load_previous_voices(sender, receiver):
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('SELECT sender, filename, timestamp FROM voice_log WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)', 
              (sender, receiver, receiver, sender))
    voice_history = c.fetchall()
    conn.close()

    decrypted_voices = []
    for voice_sender, encrypted_filename, ts in voice_history:
        try:
            decrypted_fname = cipher.decrypt(encrypted_filename).decode('utf-8')
            decrypted_voices.append((voice_sender, decrypted_fname, ts))
        except Exception as e:
            print(f"Decryption failed for voice file: {encrypted_filename}. Error: {e}")
            decrypted_voices.append((voice_sender, "[Voice Decryption Failed]", ts))

    return decrypted_voices