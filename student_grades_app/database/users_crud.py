# database/users_crud.py - CRUD cho tài khoản người dùng
import sqlite3
import pandas as pd
from utils.auth import hash_password

def create_user(conn, username, password, fullname, role, student_id=None):
    """Tạo tài khoản mới"""
    c = conn.cursor()
    try:
        hashed = hash_password(password)
        c.execute("INSERT INTO users (username, password, fullname, role, student_id) VALUES (?, ?, ?, ?, ?)",
                  (username, hashed, fullname, role, student_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users(conn):
    """Lấy danh sách tất cả users"""
    return pd.read_sql_query("SELECT id, username, fullname, role, student_id, created_at FROM users", conn)

def delete_user(conn, user_id):
    """Xóa user (trừ admin)"""
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ? AND username != 'admin'", (user_id,))
    conn.commit()