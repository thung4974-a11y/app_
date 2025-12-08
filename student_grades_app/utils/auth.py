# utils/auth.py - Xác thực người dùng
import hashlib

def hash_password(password):
    """Hash password bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(conn, username, password):
    """Xác thực đăng nhập"""
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    return c.fetchone()