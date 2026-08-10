# 💬 Connex — End-to-End Encrypted Chat Application

![Connex Banner](assets/banner.png)

> A modern, encrypted chat application built with **Python (Tkinter + Socket + SQLite)** that simulates WhatsApp-like messaging with file sharing, voice messages, and real-time online status.

---

## 🚀 Features

✅ **End-to-End Encryption** using `cryptography.fernet`  
✅ **Real-Time Messaging** via TCP sockets  
✅ **Voice Message Recording & Playback**  
✅ **File Sharing** between users  
✅ **Online/Offline User Status**  
✅ **Chat History** stored in SQLite database  
✅ **Dark Mode** support 🌙  
✅ **Custom User Display Pictures (DPs)**  
✅ **Extensible Architecture** (Server + Client separation)

---

## 🧠 Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend (GUI)** | Tkinter, Pillow |
| **Backend** | Python Socket, Threading |
| **Database** | SQLite |
| **Security** | Cryptography (Fernet) |
| **Audio** | SoundDevice, SciPy |

---

## 🧩 Project Structure

Connex/
│
├── server/
│ └── connex.py # Server program (handles all clients)
│
├── client/
│ ├── Abdul.py # Main chat client GUI
│ ├── database_utils.py # Database + encryption logic
│
├── assets/
│ ├── dps/ # Display pictures for users
│ 
│
├── README.md
├── requirements.txt
└── .gitignore


---

## ⚙️ Setup Instructions

### 🖥️ Requirements
- Python 3.10+
- Pip (Python package manager)

### 📦 Install Dependencies
```bash
pip install -r requirements.txt

🧠 Run Locally (Localhost)

1. Start the Server:

	python server/connex.py


2. Start each Client (on different terminals):

	python client/Abdul.py
	python client/Moazam.py


3. Chat, send files, and enjoy!


🔐 Security

Connex uses symmetric encryption (Fernet) to secure all messages and files.
Messages are encrypted before sending and decrypted only on the receiver side, ensuring privacy.

📈 Future Enhancements

🌍 Cloud-hosted server for real network chat

🎨 Chat themes and custom wallpapers

😊 Advanced emoji picker and stickers

📞 Audio/Video call integration

📲 Mobile version with React Native or Kivy

👨‍💻 Author

Moazam Azam
📍 Pakistan | 💻 BS-CS Student
📧 [moazamzazam389@gmail.com]
🌐 [https://github.com/Moazambuilds]

⭐ If you like this project, give it a star on GitHub!
