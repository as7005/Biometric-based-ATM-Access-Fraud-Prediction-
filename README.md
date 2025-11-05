# 🔐 Biometric ATM System
Face Recognition + Liveness + Transactions + Fraud Monitoring

A Python-based **Biometric ATM Authentication System** that verifies users using **face recognition + blink-based liveness detection**, enables ATM-like operations, and maintains logs with a **real-time dashboard for fraud monitoring**.

---

## ✅ Features
- User enrollment using webcam  
- Average face embedding stored in SQLite  
- Liveness detection using blink (Mediapipe)  
- Face recognition using stored encodings  
- ATM simulation: check balance, deposit, withdraw  
- Transaction & authentication logging  
- Dashboard for live log + fraud detection  

---

## 📂 Project Structure
├── db_init.py # Initialize DB
├── enroll.py # User enrollment + encoding
├── recognize.py # Recognition + ATM + logs
├── log_veiwer.py # Dashboard (logs + fraud)
├── requirements.txt # Dependencies
└── enroll_images/ # Captured enrollment images


---

## 🛠 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
cd <REPO_NAME>
```

2️⃣ Create a virtual environment (optional)
```bash
python -m venv venv
Activate:

# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```
3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```
⚠️ face_recognition requires dlib.
Prebuilt wheels (if needed):
https://github.com/datamagic2020/dlib-windows

📦 Database Setup
Initialize database:
```bash
python db_init.py
```

👤 User Enrollment
Capture multiple images → generate average encoding → store to database.
```bash
python enroll.py
```

Usage:
Press SPACE → capture
Press ESC → cancel
Images saved to ./enroll_images/

🔍 Recognition + ATM Operations
Performs:
- Blink-based liveness detection
- Face recognition
- ATM menu
```bash
python recognize.py
```
Menu options:
- Check balance
- Withdraw money
- Deposit money
- Exit

Logs + transactions saved to DB.

📊 Dashboard
Real-time monitoring UI (Tkinter):
- Authentication logs
- Transaction history
- Fraud alert for repeated failures
Run:
```bash
python log_veiwer.py
```


🔐 Technology Stack
Python
SQLite
OpenCV
Face Recognition (dlib)
Mediapipe
Tkinter

📄 Requirements
See requirements.txt
opencv-python
face_recognition
mediapipe
numpy
pillow

🚀 Future Improvements
QR/NFC withdrawal
Cloud server support
Improved UI
Multi-factor authentication
Smarter fraud logic

🤝 Contribution
Pull requests are welcome.
For major changes, open an issue to discuss first.

---

✅ Ready to copy-paste!  
If you'd like, I can also make:
✔ A shorter README  
✔ A more professional academic version  
✔ Badges + repo banner  

Just tell me!
