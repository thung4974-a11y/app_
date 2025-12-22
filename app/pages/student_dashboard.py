import streamlit as st
import pandas as pd
from database.grades import load_grades, get_ranking_by_semester
from utils.suggestions import generate_study_suggestions, display_study_suggestions
from pages.ranking import show_ranking

def student_dashboard(conn):
    st.sidebar.title(f"👤 {st.session_state.get('fullname','')}")
    st.sidebar.write("Vai trò: **Sinh viên**")
    
    if st.sidebar.button("🚪 Đăng xuất"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    menu = st.sidebar.radio("Menu", [
        "📋 Bảng điểm của tôi",
        "🔍 Tra cứu điểm",
        "🏆 Xếp hạng theo GPA",
        "📊 Thống kê chung"
    ])
    
    df = load_grades(conn)
    student_id = st.session_state.get('student_id', '')
    
    if menu == "📋 Bảng điểm của tôi":
        show_my_grades(df, student_id)
    elif menu == "🔍 Tra cứu điểm":
        search_grades(df)
    elif menu == "🏆 Xếp hạng theo GPA":
        show_ranking(df)
        show_my_position(df, student_id)
    elif menu == "📊 Thống kê chung":
        show_general_stats(df)

def show_my_grades(df, student_id):
    from config.subjects import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS
    
    st.title("📋 Bảng điểm của tôi")
    my_grades = df[df['mssv'] == student_id]
    
    if my_grades.empty:
        st.warning("Chưa có dữ liệu điểm của bạn.")
        return
    
    for _, row in my_grades.iterrows():
        semester = int(row.get('semester', 1))
        st.subheader(f"Học kỳ {semester}")
        
        current_subjects = SEMESTER_1_SUBJECTS if semester == 1 else SEMESTER_2_SUBJECTS
        cols = st.columns(5)
        for i, key in enumerate(current_subjects):
            with cols[i % 5]:
                score = row.get(key)
                st.metric(SUBJECTS[key]['name'][:12], f"{score:.1f}" if pd.notna(score) else "-")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Điểm TB", f"{row['diem_tb']:.2f}")
        with col2:
            st.metric("Xếp loại", row['xep_loai'])
        
        suggestions = generate_study_suggestions(row, semester)
        display_study_suggestions(suggestions, semester)
        st.divider()

def search_grades(df):
    st.title("🔍 Tra cứu điểm sinh viên")
    search_term = st.text_input("Nhập MSSV hoặc tên sinh viên")
    
    if search_term:
        results = df[
            df['mssv'].str.contains(search_term, case=False, na=False) | 
            df['student_name'].str.contains(search_term, case=False, na=False)
        ]
        if not results.empty:
            st.dataframe(
                results[['mssv', 'student_name', 'class_name', 'semester', 'diem_tb', 'xep_loai']], 
                use_container_width=True
            )
        else:
            st.info("Không tìm thấy kết quả.")

def show_my_position(df, student_id):
    if not student_id:
        return
    
    st.divider()
    st.subheader("📍 Vị trí của bạn")
    
    for sem_name, sem_val in [("Học kỳ 1", 1), ("Học kỳ 2", 2), ("Tổng hợp", 'all')]:
        ranking_df = get_ranking_by_semester(df, semester=sem_val)
        if ranking_df.empty:
            continue
        
        student_rank = ranking_df[ranking_df['mssv'] == student_id]
        if not student_rank.empty:
            rank = student_rank['xep_hang'].values[0]
            total = len(ranking_df)
            gpa = student_rank['diem_tb'].values[0]
            st.info(f"**{sem_name}:** Xếp hạng **{rank}/{total}** - Điểm TB: **{gpa:.2f}**")
        else:
            if sem_val == 'all':
                st.warning(f"**{sem_name}:** Chưa hoàn thành đủ 2 học kỳ")
            else:
                st.warning(f"**{sem_name}:** Chưa có điểm")

def show_general_stats(df):
    import plotly.express as px
    
    st.title("📊 Thống kê chung")
    
    if df.empty:
        st.warning("Chưa có dữ liệu.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng SV", df['mssv'].nunique())
    with col2:
        st.metric("Điểm TB", f"{df['diem_tb'].mean():.2f}")
    with col3:
        excellent_rate = (df['xep_loai'].isin(['Giỏi', 'Xuất sắc'])).sum() / len(df) * 100
        st.metric("Tỷ lệ Giỏi/Xuất sắc", f"{excellent_rate:.1f}%")
    with col4:
        st.metric("Số lớp", df['class_name'].nunique())
    
    fig = px.pie(df, names='xep_loai', title='Phân bố xếp loại')
    st.plotly_chart(fig, use_container_width=True)
