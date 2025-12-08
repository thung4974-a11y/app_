# dashboards/student.py - Dashboard học sinh
import streamlit as st
import pandas as pd
import plotly.express as px
from config import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS
from database.grades_crud import load_grades, get_ranking_by_semester
from pages.ranking import show_ranking

def student_dashboard(conn):
    """Dashboard cho học sinh"""
    st.sidebar.title(f"{st.session_state.get('fullname','')}")
    st.sidebar.write("Vai trò: **Học sinh**")
    
    if st.sidebar.button("Đăng xuất"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    menu = st.sidebar.radio("Menu", [
        "Bảng điểm của tôi",
        "Xếp hạng theo GPA",
        "Tra cứu điểm",
        "Thống kê chung"
    ])
    
    df = load_grades(conn)
    student_id = st.session_state.get('student_id', '')
    
    if menu == "Bảng điểm của tôi":
        _show_my_grades(df, student_id)
    elif menu == "Xếp hạng theo GPA":
        _show_student_ranking(df, student_id)
    elif menu == "Tra cứu điểm":
        _search_grades(df)
    elif menu == "Thống kê chung":
        _show_general_stats(df)

def _show_my_grades(df, student_id):
    """Hiển thị bảng điểm của sinh viên"""
    st.title("Bảng điểm của tôi")
    my_grades = df[df['mssv'] == student_id]
    
    if not my_grades.empty:
        for _, row in my_grades.iterrows():
            semester = int(row.get('semester', 1))
            st.subheader(f"Học kỳ {semester}")
            
            current_subjects = SEMESTER_1_SUBJECTS if semester == 1 else SEMESTER_2_SUBJECTS
            cols = st.columns(5)
            for i, key in enumerate(current_subjects):
                with cols[i % 5]:
                    score = row.get(key)
                    st.metric(SUBJECTS[key]['name'][:12], score if pd.notna(score) else "-")
            
            st.metric("Điểm TB", f"{row['diem_tb']:.2f}")
            st.metric("Xếp loại", row['xep_loai'])
            st.divider()
    else:
        st.warning("Chưa có dữ liệu điểm của bạn.")

def _show_student_ranking(df, student_id):
    """Hiển thị xếp hạng và vị trí của sinh viên"""
    show_ranking(df)
    
    # Hiển thị vị trí của sinh viên hiện tại
    if student_id:
        st.divider()
        st.subheader("Vị trí của bạn")
        
        for sem_name, sem_val in [("Học kỳ 1", 1), ("Học kỳ 2", 2), ("Tổng hợp", 'all')]:
            ranking_df = get_ranking_by_semester(df, semester=sem_val)
            student_rank = ranking_df[ranking_df['mssv'] == student_id]
            
            if not student_rank.empty:
                rank = student_rank['xep_hang'].values[0]
                total = len(ranking_df)
                gpa = student_rank['diem_tb'].values[0]
                st.info(f"**{sem_name}:** Xếp hạng **{rank}/{total}** - Điểm TB: **{gpa:.2f}**")

def _search_grades(df):
    """Tra cứu điểm sinh viên"""
    st.title("Tra cứu điểm sinh viên")
    search_term = st.text_input("Nhập MSSV hoặc tên sinh viên")
    
    if search_term:
        results = df[df['mssv'].str.contains(search_term, case=False, na=False) | 
                    df['student_name'].str.contains(search_term, case=False, na=False)]
        if not results.empty:
            st.dataframe(results[['mssv', 'student_name', 'class_name', 'semester', 'diem_tb', 'xep_loai']], 
                       use_container_width=True)
        else:
            st.info("Không tìm thấy kết quả.")

def _show_general_stats(df):
    """Hiển thị thống kê chung"""
    st.title("Thống kê chung")
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tổng SV", df['mssv'].nunique())
        with col2:
            st.metric("Điểm TB", f"{df['diem_tb'].mean():.2f}")
        with col3:
            excellent_rate = (df['xep_loai'] == 'Giỏi').sum() / len(df) * 100
            st.metric("Tỷ lệ Giỏi", f"{excellent_rate:.1f}%")
        with col4:
            st.metric("Số lớp", df['class_name'].nunique())
        
        fig = px.pie(df, names='xep_loai', title='Phân bố xếp loại')
        st.plotly_chart(fig, use_container_width=True)