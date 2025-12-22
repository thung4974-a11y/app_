import streamlit as st
import pandas as pd
from database.grades import get_ranking_by_semester
from utils.calculations import calculate_grade

def show_ranking(df):
    st.title("🏆 Xếp hạng theo điểm GPA")
    
    if df.empty:
        st.warning("Chưa có dữ liệu để xếp hạng.")
        return
    
    semester_option = st.radio(
        "Chọn học kỳ",
        ["Tổng hợp (cả 2 kỳ)", "Học kỳ 1", "Học kỳ 2"],
        horizontal=True
    )
    
    if semester_option == "Học kỳ 1":
        ranking_df = get_ranking_by_semester(df, semester=1)
        display_cols = ['xep_hang', 'mssv', 'student_name', 'class_name', 'diem_tb', 'xep_loai']
        col_names = ['Xếp hạng', 'MSSV', 'Họ tên', 'Lớp', 'Điểm TB', 'Xếp loại']
    elif semester_option == "Học kỳ 2":
        ranking_df = get_ranking_by_semester(df, semester=2)
        display_cols = ['xep_hang', 'mssv', 'student_name', 'class_name', 'diem_tb', 'xep_loai']
        col_names = ['Xếp hạng', 'MSSV', 'Họ tên', 'Lớp', 'Điểm TB', 'Xếp loại']
    else:
        ranking_df = get_ranking_by_semester(df, semester='all')
        display_cols = ['xep_hang', 'mssv', 'student_name', 'class_name', 'diem_tb_hk1', 'diem_tb_hk2', 'diem_tb', 'xep_loai']
        col_names = ['Xếp hạng', 'MSSV', 'Họ tên', 'Lớp', 'ĐTB HK1', 'ĐTB HK2', 'Điểm TB', 'Xếp loại']
    
    if ranking_df.empty:
        if semester_option == "Tổng hợp (cả 2 kỳ)":
            st.info("Chưa có sinh viên nào hoàn thành đủ cả 2 học kỳ.")
        else:
            st.info(f"Không có dữ liệu điểm {semester_option}.")
        return
    
    # Top 3
    show_top3(ranking_df)
    st.divider()
    
    # Bảng đầy đủ
    show_full_ranking(ranking_df, display_cols, col_names)
    
    # Thống kê
    show_ranking_stats(ranking_df)

def show_top3(ranking_df):
    st.subheader("🥇 Top 3 sinh viên xuất sắc")
    top3 = ranking_df.head(3)
    
    cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]
    colors = ["#FFD700", "#C0C0C0", "#CD7F32"]
    
    for i, (_, row) in enumerate(top3.iterrows()):
        if i < 3:
            with cols[i]:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; 
                     background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     border-radius: 10px; color: white; border: 3px solid {colors[i]};">
                    <h1>{medals[i]}</h1>
                    <h3>{row['student_name']}</h3>
                    <p><strong>MSSV:</strong> {row['mssv']}</p>
                    <p><strong>Điểm TB:</strong> {row['diem_tb']:.2f}</p>
                    <p><strong>Xếp loại:</strong> {row['xep_loai']}</p>
                </div>
                """, unsafe_allow_html=True)

def show_full_ranking(ranking_df, display_cols, col_names):
    st.subheader("📋 Bảng xếp hạng đầy đủ")
    
    col1, col2 = st.columns(2)
    with col1:
        search = st.text_input("🔍 Tìm kiếm (MSSV/Tên)", key="ranking_search")
    with col2:
        xep_loai_filter = st.selectbox(
            "Lọc theo xếp loại", 
            ['Tất cả'] + list(ranking_df['xep_loai'].dropna().unique())
        )
    
    filtered_df = ranking_df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['mssv'].astype(str).str.contains(search, case=False, na=False) |
            filtered_df['student_name'].str.contains(search, case=False, na=False)
        ]
    if xep_loai_filter != 'Tất cả':
        filtered_df = filtered_df[filtered_df['xep_loai'] == xep_loai_filter]
    
    display_df = filtered_df[display_cols].copy()
    display_df.columns = col_names
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def show_ranking_stats(ranking_df):
    st.subheader("📈 Thống kê xếp hạng")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng số SV", len(ranking_df))
    with col2:
        st.metric("Điểm TB cao nhất", f"{ranking_df['diem_tb'].max():.2f}")
    with col3:
        st.metric("Điểm TB thấp nhất", f"{ranking_df['diem_tb'].min():.2f}")
    with col4:
        excellent_count = len(ranking_df[ranking_df['xep_loai'].isin(['Giỏi', 'Xuất sắc'])])
        st.metric("Số SV Giỏi/Xuất sắc", excellent_count)
