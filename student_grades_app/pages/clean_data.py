# pages/clean_data.py - Làm sạch dữ liệu
import streamlit as st
import pandas as pd
import traceback
from config import SUBJECTS
from database.grades_crud import clean_data

def clean_data_page(conn, df):
    """Trang làm sạch dữ liệu"""
    st.title("Làm sạch dữ liệu")
    
    st.subheader("Phân tích dữ liệu hiện tại")
    
    # Đếm số bản ghi trùng
    duplicate_count = int(df.duplicated(subset=['mssv', 'semester'], keep='first').sum()) if not df.empty else 0
    
    # Đếm số điểm âm
    negative_count = 0
    for key in SUBJECTS.keys():
        if key in df.columns:
            negative_count += int((pd.to_numeric(df[key], errors='coerce') < 0).sum())
    
    col1, col2 = st.columns(2)
    with col1:
        if duplicate_count > 0:
            st.error(f"Có **{duplicate_count}** bản ghi trùng MSSV + Học kỳ")
        else:
            st.success("Không có bản ghi trùng lặp")
    
    with col2:
        if negative_count > 0:
            st.error(f"Có **{negative_count}** điểm âm (không hợp lệ)")
        else:
            st.success("Không có điểm âm")
    
    st.divider()
    
    st.subheader("Thực hiện làm sạch")
    st.write("Quá trình này sẽ:")
    st.write("- Xóa các bản ghi trùng MSSV + Học kỳ (giữ bản ghi đầu tiên)")
    st.write("- Xóa các điểm có giá trị âm")
    st.write("- Tính lại điểm TB và xếp loại")
    
    if st.button("Làm sạch dữ liệu", type="primary", 
                disabled=(duplicate_count == 0 and negative_count == 0)):
        try:
            duplicates_removed, negatives_fixed = clean_data(conn)
            st.success(f"Hoàn thành! Đã xóa {duplicates_removed} bản ghi trùng và sửa {negatives_fixed} điểm âm.")
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi khi làm sạch: {e}")
            print(traceback.format_exc())