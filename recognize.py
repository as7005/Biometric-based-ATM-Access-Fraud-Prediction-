import cv2
import numpy as np
import sqlite3
import face_recognition
import mediapipe as mp
from datetime import datetime
import time

DB_PATH = "biometric_atm.db"

# ========== DATABASE FUNCTIONS ==========

def init_db():
    """Ensure logs and transactions tables exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            amount REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()


def load_known_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, encoding FROM users")
    rows = c.fetchall()
    conn.close()

    names, encodings = [], []
    for name, enc_blob in rows:
        enc = np.frombuffer(enc_blob, dtype=np.float64)
        names.append(name)
        encodings.append(enc)
    print(f"[INFO] Loaded {len(names)} known users from DB.")
    return names, encodings


def log_event(name, status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO logs (name, status, timestamp) VALUES (?, ?, ?)",
              (name, status, timestamp))
    conn.commit()
    conn.close()
    print(f"[LOG] {status} - {name} at {timestamp}")


def log_transaction(name, tx_type, amount):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO transactions (name, type, amount, timestamp) VALUES (?, ?, ?, ?)",
              (name, tx_type, amount, timestamp))
    conn.commit()
    conn.close()
    print(f"[TX] {tx_type} of ₹{amount} logged for {name}")


# ========== LIVENESS DETECTION ==========

def detect_blink(frame, mesh):
    """Detects if eyes are closed momentarily (blink)."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mesh.process(rgb)
    if not results.multi_face_landmarks:
        return False

    # Using landmark indices for left/right eyes
    L_UP, L_DOWN = 159, 145
    R_UP, R_DOWN = 386, 374

    for face in results.multi_face_landmarks:
        landmarks = face.landmark
        l_up = landmarks[L_UP]
        l_down = landmarks[L_DOWN]
        r_up = landmarks[R_UP]
        r_down = landmarks[R_DOWN]

        l_dist = abs(l_up.y - l_down.y)
        r_dist = abs(r_up.y - r_down.y)

        if l_dist < 0.01 and r_dist < 0.01:
            return True
    return False


# ========== ATM MENU SIMULATION ==========

def atm_menu(user_name):
    balance = 10000.0  # starting balance for demo
    print("\n====================================")
    print(f"💳 Welcome, {user_name}! Access Granted.")
    print("====================================")

    while True:
        print("\nSelect an option:")
        print("1. Check Balance")
        print("2. Withdraw Money")
        print("3. Deposit Money")
        print("4. Exit")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            print(f"💰 Your current balance is: ₹{balance:.2f}")

        elif choice == "2":
            amt = float(input("Enter amount to withdraw: ₹"))
            if amt <= balance:
                balance -= amt
                print(f"✅ Withdrawal successful! Remaining balance: ₹{balance:.2f}")
                log_transaction(user_name, "Withdraw", amt)
            else:
                print("❌ Insufficient balance!")

        elif choice == "3":
            amt = float(input("Enter amount to deposit: ₹"))
            balance += amt
            print(f"✅ Deposit successful! New balance: ₹{balance:.2f}")
            log_transaction(user_name, "Deposit", amt)

        elif choice == "4":
            print("🔒 Session ended. Thank you for using Biometric ATM.")
            break

        else:
            print("Invalid choice. Try again.")


# ========== RECOGNITION FUNCTION ==========

def run_recognition():
    init_db()
    known_names, known_encodings = load_known_users()
    if not known_encodings:
        print("[ERROR] No known users found!")
        return

    cap = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

    print("[INFO] Please blink once to verify liveness...")
    blink_detected = False
    start = time.time()

    while time.time() - start < 10:
        ret, frame = cap.read()
        if not ret:
            continue

        if detect_blink(frame, mp_face_mesh):
            blink_detected = True
            print("[INFO] Blink detected ✅ Liveness confirmed.")
            break

        cv2.imshow("Liveness Detection (Blink to continue)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if not blink_detected:
        print("[ERROR] Liveness check failed. Please try again.")
        log_event("Unknown", "Failed (No Liveness)")
        return

    # ========== FACE RECOGNITION SECTION ==========
    cap = cv2.VideoCapture(0)
    print("[INFO] Face recognition starting... Look at the camera.")

    identified_user = None
    no_match_frames = 0
    MAX_NO_MATCH_FRAMES = 20  # frames before deciding no match
    THRESHOLD = 0.35

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame = np.ascontiguousarray(rgb_frame)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Case 1: No face detected
        if len(face_encodings) == 0:
            no_match_frames += 1
            if no_match_frames == MAX_NO_MATCH_FRAMES:
                print("❌ No face detected. Please position yourself properly or register first.")
                log_event("Unknown", "Failed (No Face Detected)")
                break
            continue

        match_found = False
        for face_encoding in face_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            print(f"[DEBUG] Closest match distance: {best_distance:.3f}")

            if best_distance < THRESHOLD:
                identified_user = known_names[best_match_index]
                match_found = True
                break

        if match_found:
            log_event(identified_user, "Success")
            print(f"\n[SUCCESS] Welcome {identified_user}!")
            break

        # Case 2: No match found after several frames
        no_match_frames += 1
        if no_match_frames >= MAX_NO_MATCH_FRAMES:
            print("❌ Face not found in database. Please register before using the ATM.")
            log_event("Unknown", "Failed (Unregistered Face)")
            break

        cv2.imshow("Recognizing...", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if identified_user:
        atm_menu(identified_user)
    else:
        print("[INFO] Session ended — unrecognized or unregistered user.")


if __name__ == "__main__":
    run_recognition()
