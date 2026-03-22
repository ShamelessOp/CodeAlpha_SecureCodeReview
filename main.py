#!/usr/bin/env python3
"""
vulnerable_app.py
A deliberately insecure Python web-like application used as the audit target
for CodeAlpha Task 3 — Secure Coding Review.
DO NOT deploy this in production. For educational purposes only.
"""

import sqlite3
import hashlib
import subprocess
import pickle
import os
import re

# ── VULNERABILITY 1: Hardcoded credentials ────────────────────────────────────
SECRET_KEY  = "supersecret123"          # CWE-798
DB_PASSWORD = "admin123"               # CWE-798
API_KEY     = "sk-abcd1234hardcoded"   # CWE-798

# ── VULNERABILITY 2: Insecure database initialisation ─────────────────────────
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)""")
    # Storing plain MD5 password — CWE-916
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'md5hash', 'admin')")
    conn.commit()
    return conn

# ── VULNERABILITY 3: SQL Injection ────────────────────────────────────────────
def login(username, password):
    conn = init_db()
    c = conn.cursor()
    # Direct string interpolation — CWE-89
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    c.execute(query)
    return c.fetchone()

# ── VULNERABILITY 4: Weak password hashing ────────────────────────────────────
def hash_password(password):
    # MD5 is cryptographically broken — CWE-916
    return hashlib.md5(password.encode()).hexdigest()

# ── VULNERABILITY 5: Command Injection ────────────────────────────────────────
def ping_host(host):
    # shell=True with user input — CWE-78
    result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True)
    return result.stdout

# ── VULNERABILITY 6: Insecure Deserialisation ─────────────────────────────────
def load_user_session(session_data):
    # Unpickling untrusted data — CWE-502
    return pickle.loads(session_data)

# ── VULNERABILITY 7: Path Traversal ───────────────────────────────────────────
def read_file(filename):
    # No sanitisation — CWE-22
    with open(f"/var/www/uploads/{filename}", "r") as f:
        return f.read()

# ── VULNERABILITY 8: Sensitive data in logs ───────────────────────────────────
def log_login(username, password):
    # Logging credentials in plaintext — CWE-312
    print(f"[LOG] Login attempt: username={username} password={password}")

# ── VULNERABILITY 9: Missing input validation ──────────────────────────────────
def register_user(username, email, password):
    conn = init_db()
    c = conn.cursor()
    # No validation of email format, no password strength check — CWE-20
    hashed = hash_password(password)
    c.execute(f"INSERT INTO users VALUES (NULL, '{username}', '{hashed}', 'user')")
    conn.commit()

# ── VULNERABILITY 10: Insecure random token ───────────────────────────────────
def generate_token():
    import random  # Not cryptographically secure — CWE-338
    return str(random.randint(100000, 999999))

# ── VULNERABILITY 11: XSS via template rendering ──────────────────────────────
def render_profile(username):
    # Directly embedding user input into HTML — CWE-79
    return f"<h1>Welcome, {username}!</h1>"

# ── VULNERABILITY 12: Debug mode / info disclosure ────────────────────────────
DEBUG = True   # Should never be True in production — CWE-215

if __name__ == "__main__":
    print("Vulnerable app running... (for audit purposes only)")
