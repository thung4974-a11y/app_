# database/grades_crud.py - CRUD cho điểm sinh viên
import pandas as pd
import numpy as np
import traceback
from config import SUBJECTS, ACADEMIC_YEAR
from utils.calculations import calculate_average, calculate_grade

def load_grades(conn):
    """Load tất cả điểm từ database"""
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
    """Lưu điểm mới vào database"""
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
    """Xóa điểm theo ID"""
    c = conn.cursor()
    c.execute("DELETE FROM grades WHERE id = ?", (grade_id,))
    conn.commit()

def get_combined_grades(df):
    """Gộp sinh viên có 2 kỳ thành 1 dòng với điểm TB cả 2 kỳ"""
    if df.empty:
        return df
    
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
                'id': f"{sem1_row['id']},{sem2_row['id']}",
                'mssv': mssv,
                'student_name': sem1_row['student_name'],
                'class_name': sem1_row['class_name'],
                'semester': '1 + 2',
                'diem_tb': diem_tb_combined,
                'xep_loai': calculate_grade(diem_tb_combined),
                'diem_tb_hk1': diem_tb_1,
                'diem_tb_hk2': diem_tb_2
            })
        else:
            for _, row in group.iterrows():
                combined_rows.append({
                    'id': row['id'],
                    'mssv': row['mssv'],
                    'student_name': row['student_name'],
                    'class_name': row['class_name'],
                    'semester': str(int(row['semester'])),
                    'diem_tb': row['diem_tb'],
                    'xep_loai': row['xep_loai'],
                    'diem_tb_hk1': row['diem_tb'] if row['semester'] == 1 else None,
                    'diem_tb_hk2': row['diem_tb'] if row['semester'] == 2 else None
                })
    
    return pd.DataFrame(combined_rows)

def get_ranking_by_semester(df, semester=None):
    """Xếp hạng sinh viên theo điểm GPA, chia theo từng kỳ"""
    if df.empty:
        return df
    
    if semester == 'all' or semester is None:
        combined = get_combined_grades(df)
        combined = combined.sort_values('diem_tb', ascending=False).reset_index(drop=True)
        combined['xep_hang'] = range(1, len(combined) + 1)
        return combined
    else:
        semester_df = df[df['semester'] == semester].copy()
        semester_df = semester_df.sort_values('diem_tb', ascending=False).reset_index(drop=True)
        semester_df['xep_hang'] = range(1, len(semester_df) + 1)
        return semester_df

def clean_data(conn):
    """Làm sạch dữ liệu: xóa trùng MSSV+semester, sửa điểm âm"""
    df = load_grades(conn)
    c = conn.cursor()
    
    original_count = len(df)
    
    if original_count == 0:
        return 0, 0
    
    for key in SUBJECTS.keys():
        if key in df.columns:
            df[key] = pd.to_numeric(df[key], errors='coerce')
    
    negative_fixed = 0
    for key in SUBJECTS.keys():
        if key in df.columns:
            negative_count = int((df[key] < 0).sum())
            negative_fixed += negative_count
            df.loc[df[key] < 0, key] = np.nan
    
    df_clean = df.drop_duplicates(subset=['mssv', 'semester'], keep='first')
    duplicates_removed = original_count - len(df_clean)
    
    try:
        c.execute("DELETE FROM grades")
        inserted = 0
        for _, row in df_clean.iterrows():
            diem_tb = calculate_average(row)
            xep_loai = calculate_grade(diem_tb)
            
            def safe_val(k):
                v = row.get(k)
                if pd.isna(v):
                    return None
                return float(v) if v != '' else None
            
            params = (
                row.get('mssv', ''), row.get('student_name', ''), row.get('class_name', None),
                int(row.get('semester', 1)) if not pd.isna(row.get('semester', 1)) else 1,
                safe_val('triet'), safe_val('giai_tich_1'), safe_val('giai_tich_2'),
                safe_val('tieng_an_do_1'), safe_val('tieng_an_do_2'),
                safe_val('gdtc'), safe_val('thvp'), safe_val('tvth'),
                safe_val('phap_luat'), safe_val('logic'),
                float(diem_tb), xep_loai, int(ACADEMIC_YEAR)
            )
            try:
                c.execute('''INSERT INTO grades (mssv, student_name, class_name, semester,
                             triet, giai_tich_1, giai_tich_2, tieng_an_do_1, tieng_an_do_2,
                             gdtc, thvp, tvth, phap_luat, logic,
                             diem_tb, xep_loai, academic_year)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', params)
                inserted += 1
            except Exception as e:
                print("Error inserting row during clean_data:", e)
                print(traceback.format_exc())
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error in clean_data main:", e)
        print(traceback.format_exc())
        raise
    
    return duplicates_removed, negative_fixed