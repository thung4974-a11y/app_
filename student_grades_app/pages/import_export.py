# pages/import_export.py - Import/Export dữ liệu
import streamlit as st
import pandas as pd
import numpy as np
import traceback
from config import SUBJECTS, ACADEMIC_YEAR
from utils.calculations import calculate_average, calculate_grade

def import_data(conn):
    """Trang import dữ liệu từ CSV"""
    st.title("Import dữ liệu")
    
    st.info(f"""
    **Định dạng file CSV cần có các cột:**
    - mssv, student_name, class_name, semester
    - {', '.join(SUBJECTS.keys())}
    
    **Lưu ý:** 
    - Học kỳ (semester) = 1 hoặc 2
    - Năm học cố định = {ACADEMIC_YEAR}
    - GDTC không tính vào GPA
    """)
    
    uploaded_file = st.file_uploader("Chọn file CSV", type=['csv'])
    
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            st.write("**Xem trước dữ liệu:**")
            st.dataframe(df.head(10))
            
            if st.button("Import vào database"):
                c = conn.cursor()
                
                for key in SUBJECTS.keys():
                    if key in df.columns:
                        df[key] = pd.to_numeric(df[key], errors='coerce')
                    else:
                        df[key] = np.nan
                
                count_inserted = 0
                for _, row in df.iterrows():
                    diem_tb = calculate_average(row)
                    xep_loai = calculate_grade(diem_tb)
                    semester = int(row.get('semester', 1)) if not pd.isna(row.get('semester', 1)) else 1
                    
                    params = (
                        row.get('mssv', ''), row.get('student_name', ''), row.get('class_name', ''),
                        semester,
                        None if pd.isna(row.get('triet')) else float(row.get('triet')),
                        None if pd.isna(row.get('giai_tich_1')) else float(row.get('giai_tich_1')),
                        None if pd.isna(row.get('giai_tich_2')) else float(row.get('giai_tich_2')),
                        None if pd.isna(row.get('tieng_an_do_1')) else float(row.get('tieng_an_do_1')),
                        None if pd.isna(row.get('tieng_an_do_2')) else float(row.get('tieng_an_do_2')),
                        None if pd.isna(row.get('gdtc')) else float(row.get('gdtc')),
                        None if pd.isna(row.get('thvp')) else float(row.get('thvp')),
                        None if pd.isna(row.get('tvth')) else float(row.get('tvth')),
                        None if pd.isna(row.get('phap_luat')) else float(row.get('phap_luat')),
                        None if pd.isna(row.get('logic')) else float(row.get('logic')),
                        float(diem_tb), xep_loai, int(ACADEMIC_YEAR)
                    )
                    try:
                        c.execute('''INSERT INTO grades (mssv, student_name, class_name, semester,
                                     triet, giai_tich_1, giai_tich_2, tieng_an_do_1, tieng_an_do_2,
                                     gdtc, thvp, tvth, phap_luat, logic,
                                     diem_tb, xep_loai, academic_year)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', params)
                        count_inserted += 1
                    except Exception as e:
                        print("Error inserting row during import:", e)
                        print(traceback.format_exc())
                conn.commit()
                st.success(f"Đã import ~{count_inserted} bản ghi!")
                st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi đọc file: {e}")
            print(traceback.format_exc())

def export_data(df):
    """Trang export dữ liệu ra CSV"""
    st.title("Export dữ liệu")
    
    if df.empty:
        st.warning("Không có dữ liệu để export.")
        return
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("Tải file CSV", csv, "student_grades.csv", "text/csv")