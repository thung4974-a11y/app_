# database/grades.py - CRUD Điểm

import pandas as pd
import numpy as np
from config.subjects import SUBJECTS, ACADEMIC_YEAR
from utils.calculations import calculate_average, calculate_grade

def load_grades(conn):
    try:
        df = pd.read_sql_query("SELECT * FROM grades", conn)
        for key in SUBJECTS.keys():
            if key in df.columns:
                df[key] = pd.to_numeric(df[key], errors='coerce')
        if 'diem_tb' in df.columns:
            df['diem_tb'] = pd.to_numeric(df['diem_tb'], errors='coerce').fillna(0.0)
        return df
    except Exception:
        cols = ['id','mssv','student_name','class_name','semester'] + list(SUBJECTS.keys()) + ['diem_tb','xep_loai','academic_year','updated_at']
        return pd.DataFrame(columns=cols)

def save_grade(conn, data):
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO grades (mssv, student_name, class_name, semester, 
                     triet, giai_tich_1, giai_tich_2, tieng_an_do_1, tieng_an_do_2,
                     gdtc, thvp, tvth, phap_luat, logic,
                     diem_tb, xep_loai, academic_year)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)

def delete_grade(conn, grade_id):
    c = conn.cursor()
    c.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    conn.commit()

def delete_grades_batch(conn, grade_ids):
    c = conn.cursor()
    for grade_id in grade_ids:
        c.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    conn.commit()

def get_ranking_by_semester(df, semester=None):
    """Xếp hạng sinh viên theo điểm GPA"""
    if df.empty:
        return pd.DataFrame()
    
    if semester == 'all' or semester is None:
        grouped = df.groupby('mssv')
        combined_rows = []
        
        for mssv, group in grouped:
            semesters = group['semester'].unique().tolist()
            if len(semesters) == 2 and 1 in semesters and 2 in semesters:
                sem1_row = group[group['semester'] == 1].iloc[0]
                sem2_row = group[group['semester'] == 2].iloc[0]
                
                diem_tb_1 = float(sem1_row['diem_tb']) if pd.notna(sem1_row['diem_tb']) else 0
                diem_tb_2 = float(sem2_row['diem_tb']) if pd.notna(sem2_row['diem_tb']) else 0
                diem_tb_combined = round((diem_tb_1 + diem_tb_2) / 2, 2)
                
                combined_rows.append({
                    'mssv': mssv,
                    'student_name': sem1_row['student_name'],
                    'class_name': sem1_row['class_name'],
                    'semester': 'Cả 2 kỳ',
                    'diem_tb': diem_tb_combined,
                    'xep_loai': calculate_grade(diem_tb_combined),
                    'diem_tb_hk1': diem_tb_1,
                    'diem_tb_hk2': diem_tb_2
                })
        
        if not combined_rows:
            return pd.DataFrame()
        
        result_df = pd.DataFrame(combined_rows)
        result_df = result_df.sort_values('diem_tb', ascending=False).reset_index(drop=True)
        result_df['xep_hang'] = range(1, len(result_df) + 1)
        return result_df
    else:
        semester_df = df[df['semester'] == semester].copy()
        if semester_df.empty:
            return pd.DataFrame()
        semester_df = semester_df.sort_values('diem_tb', ascending=False).reset_index(drop=True)
        semester_df['xep_hang'] = range(1, len(semester_df) + 1)
        return semester_df

def can_take_semester_2(conn, mssv):
    df = load_grades(conn)
    student_sem1 = df[(df['mssv'] == mssv) & (df['semester'] == 1)]
    
    if student_sem1.empty:
        return False, "Chưa có điểm học kỳ 1"
    
    row = student_sem1.iloc[0]
    try:
        giai_tich_1 = float(row.get('giai_tich_1') or 0)
    except Exception:
        giai_tich_1 = 0
    try:
        tieng_an_do_1 = float(row.get('tieng_an_do_1') or 0)
    except Exception:
        tieng_an_do_1 = 0
    avg = (giai_tich_1 + tieng_an_do_1) / 2.0
    
    if avg >= 4:
        return True, f"Đủ điều kiện (TB: {avg:.2f})"
    else:
        return False, f"Chưa đủ điều kiện (TB: {avg:.2f} < 4)"
