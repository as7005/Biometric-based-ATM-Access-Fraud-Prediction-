import cv2
import os
import numpy as np
import face_recognition
import sqlite3

# ========== CONFIGURATION ==========
DB_PATH = "biometric_atm.db"
ENROLL_DIR = "enroll_images"

# ===================================

def init_db():
    """Ensure database and table exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            encoding BLOB NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def capture_images(user_name, num_images=5):
    """Capture face images from webcam."""
    os.makedirs(ENROLL_DIR, exist_ok=True)
    cap = cv2.VideoCapture(0)

    print(f"[INFO] Capturing {num_images} images for {user_name}. Press SPACE to capture, ESC to exit.")

    count = 0
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read from camera.")
            break

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1)

        if key % 256 == 27:  # ESC key
            print("[INFO] Capture cancelled.")
            break
        elif key % 256 == 32:  # SPACE key
            img_path = os.path.join(ENROLL_DIR, f"{user_name}_{count + 1}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"[INFO] Saved {img_path}")
            count += 1

    cap.release()
    cv2.destroyAllWindows()


def create_average_encoding(image_paths):
    """Generate an average face encoding from multiple images."""
    encodings = []

    for p in image_paths:
        print(f"[DEBUG] Processing image: {p}")
        img_bgr = cv2.imread(p)
        if img_bgr is None:
            print("[ERROR] Could not read image:", p)
            continue

        # Handle transparency if 4-channel (BGRA)
        if img_bgr.ndim == 3 and img_bgr.shape[2] == 4:
            img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2BGR)

        # Convert BGR → RGB
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Ensure 8-bit and contiguous memory (critical for dlib)
        img_rgb = np.ascontiguousarray(img_rgb, dtype=np.uint8)

        print(f"[DEBUG] dtype={img_rgb.dtype}, shape={img_rgb.shape}")

        try:
            boxes = face_recognition.face_locations(img_rgb, model="hog")
            if len(boxes) == 0:
                print("[WARN] No face detected in", p)
                continue

            encs = face_recognition.face_encodings(img_rgb, boxes)
            if len(encs) == 0:
                print("[WARN] No encodings generated for", p)
                continue

            encodings.append(encs[0])

        except Exception as e:
            print("[ERROR] Face encoding failed:", e)

    if not encodings:
        raise ValueError("No valid face encodings found!")

    avg_encoding = np.mean(encodings, axis=0)
    return avg_encoding


def save_encoding_to_db(name, encoding):
    """Store encoding in SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (name, encoding) VALUES (?, ?)", (name, encoding.tobytes()))
    conn.commit()
    conn.close()
    print(f"[INFO] Stored user '{name}' in DB.")


def main():
    init_db()
    user_name = input("Enter user name to enroll (no spaces): ").strip()
    if not user_name:
        print("[ERROR] Invalid user name.")
        return

    capture_images(user_name)
    image_paths = [os.path.join(ENROLL_DIR, f) for f in os.listdir(ENROLL_DIR) if f.startswith(user_name)]

    if not image_paths:
        print("[ERROR] No images captured for", user_name)
        return

    try:
        encoding = create_average_encoding(image_paths)
        
        save_encoding_to_db(user_name, encoding)
        print("[SUCCESS] Enrollment complete.")
    except Exception as e:
        print("Error creating encoding:", e)


if __name__ == "__main__":
    main()
