# database/connection.py - Kết nối Database

import sqlite3
import hashlib

def init_db(db_path='student_grades.db'):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        fullname TEXT NOT NULL,
        role TEXT NOT NULL,
        student_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mssv TEXT NOT NULL,
        student_name TEXT NOT NULL,
        class_name TEXT,
        semester INTEGER DEFAULT 1,
        triet REAL,
        giai_tich_1 REAL,
        giai_tich_2 REAL,
        tieng_an_do_1 REAL,
        tieng_an_do_2 REAL,
        gdtc REAL,
        thvp REAL,
        tvth REAL,
        phap_luat REAL,
        logic REAL,
        diem_tb REAL,
        xep_loai TEXT,
        academic_year INTEGER DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tạo admin mặc định
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute("INSERT INTO users (username, password, fullname, role) VALUES (?, ?, ?, ?)",
                  ('admin', admin_pass, 'Quản trị viên', 'teacher'))
    
    conn.commit()
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(conn, username, password):
    c = conn.cursor()
    hashed = hash_password(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed))
    return c.fetchone()
