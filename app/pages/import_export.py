import streamlit as st
import pandas as pd
import numpy as np
from config.subjects import SUBJECTS, ACADEMIC_YEAR
from utils.calculations import calculate_average, calculate_grade

def import_data(conn):
    st.title("📥 Import dữ liệu")
    
    option = st.radio(
        "Chọn loại dữ liệu cần nhập:",
        ["Học kỳ 1", "Học kỳ 2", "Cả hai kỳ"],
        horizontal=True
    )
    
    show_format_info(option)
    
    uploaded_file = st.file_uploader("📁 Chọn file CSV", type=['csv'])
    
    if uploaded_file:
        process_uploaded_file(conn, uploaded_file, option)

def show_format_info(option):
    if option == "Học kỳ 1":
        st.info("Định dạng: mssv, student_name, class_name, semester(=1), triet, giai_tich_1, tieng_an_do_1, gdtc, thvp")
    elif option == "Học kỳ 2":
        st.info("Định dạng: mssv, student_name, class_name, semester(=2), giai_tich_2, tieng_an_do_2, tvth, phap_luat, logic")
    else:
        st.info("Định dạng: mssv, student_name, class_name, semester, [các môn theo kỳ]")

def process_uploaded_file(conn, uploaded_file, option):
    try:
        df = pd.read_csv(uploaded_file)
        st.write("📋 Xem trước dữ liệu:")
        st.dataframe(df.head(10))
        
        if st.button("📥 Import vào database", type="primary"):
            count = import_to_database(conn, df, option)
            st.success(f"Đã import {count} bản ghi thành công!")
            st.rerun()
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")

def import_to_database(conn, df, option):
    c = conn.cursor()
    
    for key in SUBJECTS.keys():
        if key not in df.columns:
            df[key] = np.nan
        else:
            df[key] = pd.to_numeric(df[key], errors='coerce')
    
    count_inserted = 0
    
    for _, row in df.iterrows():
        semester = int(row.get("semester", 1))
        
        if option == "Học kỳ 1" and semester != 1:
            continue
        if option == "Học kỳ 2" and semester != 2:
            continue
        
        diem_tb = calculate_average(row)
        xep_loai = calculate_grade(diem_tb)
        
        params = (
            row.get('mssv', ''), row.get('student_name', ''), row.get('class_name', ''),
            semester,
            None if pd.isna(row['triet']) else float(row['triet']),
            None if pd.isna(row['giai_tich_1']) else float(row['giai_tich_1']),
            None if pd.isna(row['giai_tich_2']) else float(row['giai_tich_2']),
            None if pd.isna(row['tieng_an_do_1']) else float(row['tieng_an_do_1']),
            None if pd.isna(row['tieng_an_do_2']) else float(row['tieng_an_do_2']),
            None if pd.isna(row['gdtc']) else float(row['gdtc']),
            None if pd.isna(row['thvp']) else float(row['thvp']),
            None if pd.isna(row['tvth']) else float(row['tvth']),
            None if pd.isna(row['phap_luat']) else float(row['phap_luat']),
            None if pd.isna(row['logic']) else float(row['logic']),
            float(diem_tb), xep_loai, int(ACADEMIC_YEAR)
        )
        
        try:
            c.execute('''INSERT INTO grades (mssv, student_name, class_name, semester,
                         triet, giai_tich_1, giai_tich_2, tieng_an_do_1, tieng_an_do_2,
                         gdtc, thvp, tvth, phap_luat, logic,
                         diem_tb, xep_loai, academic_year)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', params)
            count_inserted += 1
        except Exception:
            pass
    
    conn.commit()
    return count_inserted

def export_data(df):
    st.title("📤 Export dữ liệu")
    
    if df.empty:
        st.warning("Không có dữ liệu để export.")
        return
    
    st.write(f"📊 Tổng số bản ghi: {len(df)}")
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📥 Tải file CSV", 
        csv, 
        "student_grades.csv", 
        "text/csv",
        type="primary"
    )
