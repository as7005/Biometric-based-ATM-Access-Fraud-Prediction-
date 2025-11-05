import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta


DB_PATH = "biometric_atm.db"


# ========== DATABASE FETCH FUNCTIONS ==========

def fetch_logs():
    """Fetch authentication logs from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, status, timestamp FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_transactions():
    """Fetch transaction logs from the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, type, amount, timestamp FROM transactions ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows


def detect_fraud():
    """Detect if 3+ failed attempts occurred within 5 minutes."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    time_threshold = datetime.now() - timedelta(minutes=5)
    c.execute("SELECT COUNT(*) FROM logs WHERE status LIKE 'Failed%' AND timestamp > ?", 
              (time_threshold.strftime("%Y-%m-%d %H:%M:%S"),))
    count = c.fetchone()[0]
    conn.close()
    return count >= 3


# ========== UI REFRESH FUNCTIONS ==========

def refresh_logs():
    for row in log_tree.get_children():
        log_tree.delete(row)
    for log in fetch_logs():
        log_tree.insert("", "end", values=log)
    root.after(5000, refresh_logs)  # auto-refresh every 5s


def refresh_transactions():
    for row in tx_tree.get_children():
        tx_tree.delete(row)
    for tx in fetch_transactions():
        tx_tree.insert("", "end", values=tx)
    root.after(5000, refresh_transactions)


def refresh_fraud_status():
    if detect_fraud():
        fraud_label.config(text="⚠️ FRAUD ALERT: Multiple failed attempts detected!", fg="#ff4d4d")
    else:
        fraud_label.config(text="System Status: Normal ✅", fg="#00ff99")
    root.after(5000, refresh_fraud_status)


# ========== UI SETUP ==========

def setup_ui():
    global root, log_tree, tx_tree, fraud_label

    root = tk.Tk()
    root.title("Biometric ATM Monitoring Dashboard")
    root.geometry("800x500")
    root.configure(bg="#1e1e1e")

    title = tk.Label(root, text="💳 Biometric ATM Access & Fraud Prevention Dashboard",
                     font=("Segoe UI", 18, "bold"),
                     fg="#00ffff", bg="#1e1e1e")
    title.pack(pady=10)

    fraud_label = tk.Label(root, text="System Status: Normal ✅", 
                           font=("Segoe UI", 14, "bold"),
                           fg="#00ff99", bg="#1e1e1e")
    fraud_label.pack(pady=5)

    # Tabs for logs and transactions
    tab_control = ttk.Notebook(root)
    log_tab = ttk.Frame(tab_control)
    tx_tab = ttk.Frame(tab_control)
    tab_control.add(log_tab, text="Authentication Logs")
    tab_control.add(tx_tab, text="Transaction History")
    tab_control.pack(expand=1, fill="both")

    # Style
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2e2e2e", fieldbackground="#2e2e2e", 
                    foreground="white", rowheight=25)
    style.map("Treeview", background=[("selected", "#00ffff")])

    # Log Table
    log_columns = ("ID", "Name", "Status", "Timestamp")
    log_tree = ttk.Treeview(log_tab, columns=log_columns, show="headings")
    for col in log_columns:
        log_tree.heading(col, text=col)
        log_tree.column(col, anchor="center", width=180)
    log_tree.pack(padx=10, pady=10, fill="both", expand=True)

    # Transaction Table
    tx_columns = ("ID", "Name", "Type", "Amount", "Timestamp")
    tx_tree = ttk.Treeview(tx_tab, columns=tx_columns, show="headings")
    for col in tx_columns:
        tx_tree.heading(col, text=col)
        tx_tree.column(col, anchor="center", width=160)
    tx_tree.pack(padx=10, pady=10, fill="both", expand=True)

    # Start automatic refresh
    refresh_logs()
    refresh_transactions()
    refresh_fraud_status()

    root.mainloop()


if __name__ == "__main__":
    setup_ui()
