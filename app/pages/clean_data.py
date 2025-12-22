import streamlit as st
import pandas as pd
from database.grades import clean_data
from config.subjects import SUBJECTS

def clean_data_page(conn, df):
    st.title("🧹 Làm sạch dữ liệu")
    
    st.subheader("📊 Phân tích dữ liệu hiện tại")
    
    duplicate_semester = int(df.duplicated(subset=['mssv', 'semester'], keep='first').sum()) if not df.empty else 0
    
    duplicate_name = 0
    if not df.empty:
        name_conflict_groups = df.groupby("mssv")["student_name"].nunique()
        duplicate_name = int((name_conflict_groups > 1).sum())
    
    negative_count = 0
    for key in SUBJECTS.keys():
        if key in df.columns:
            negative_count += int((pd.to_numeric(df[key], errors='coerce') < 0).sum())
    
    col1, col2 = st.columns(2)
    with col1:
        if duplicate_semester > 0 or duplicate_name > 0:
            st.error(f"- {duplicate_semester} bản ghi trùng **MSSV + Học kỳ**\n- {duplicate_name} MSSV có **nhiều tên khác nhau**")
        else:
            st.success("✅ Không có bản ghi trùng lặp")
    
    with col2:
        if negative_count > 0:
            st.error(f"❌ Có **{negative_count}** điểm âm (không hợp lệ)")
        else:
            st.success("✅ Không có điểm âm")
    
    st.divider()
    
    st.subheader("🔧 Thực hiện làm sạch")
    st.write("""
    Quá trình này sẽ:
    - Xóa các bản ghi trùng **MSSV + Học kỳ** (giữ bản ghi đầu tiên)
    - Xóa các bản ghi **MSSV có nhiều tên**, giữ tên xuất hiện nhiều nhất
    - Xóa các điểm có giá trị âm
    - Tính lại điểm TB và xếp loại
    """)
    
    has_issues = duplicate_semester > 0 or duplicate_name > 0 or negative_count > 0
    
    if st.button("🧹 Làm sạch dữ liệu", type="primary", disabled=not has_issues):
        try:
            duplicates_removed, name_removed, negatives_fixed = clean_data(conn)
            st.success(f"""
            ✅ Hoàn thành!
            - Xóa {duplicates_removed} bản ghi trùng MSSV + học kỳ
            - Xóa {name_removed} bản ghi do MSSV có nhiều tên
            - Sửa {negatives_fixed} điểm âm
            """)
            st.rerun()
        except Exception as e:
            st.error(f"Lỗi: {e}")
