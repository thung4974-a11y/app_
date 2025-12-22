# pages/teacher_dashboard.py - Dashboard giáo viên

import streamlit as st
from database.grades import load_grades
from pages.ranking import show_ranking
from pages.charts import show_charts
from pages.grades_management import manage_grades_new, add_grade_form
from pages.data_operations import import_data, export_data, clean_data_page
from pages.user_management import manage_users
from pages.powerbi import show_powerbi_page

def teacher_dashboard(conn):
    st.sidebar.title(f"{st.session_state.get('fullname','')}")
    st.sidebar.write("Vai trò: **Giáo viên**")
    
    if st.sidebar.button("Đăng xuất", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    menu = st.sidebar.radio("Menu", [
        "Dashboard",
        "Quản lý điểm",
        "Xếp hạng theo GPA",
        "Thêm điểm",
        "Import dữ liệu",
        "Export dữ liệu",
        "Làm sạch dữ liệu",
        "Quản lý tài khoản",
        "Biểu đồ phân tích",
        "📊 Power BI"  # MỚI
    ])
    
    df = load_grades(conn)
    
    if menu == "Dashboard":
        show_dashboard(df)
    elif menu == "Quản lý điểm":
        manage_grades_new(conn, df)
    elif menu == "Xếp hạng theo GPA":
        show_ranking(df)
    elif menu == "Thêm điểm":
        add_grade_form(conn)
    elif menu == "Import dữ liệu":
        import_data(conn)
    elif menu == "Export dữ liệu":
        export_data(df)
    elif menu == "Làm sạch dữ liệu":
        clean_data_page(conn, df)
    elif menu == "Quản lý tài khoản":
        manage_users(conn)
    elif menu == "Biểu đồ phân tích":
        show_charts(df)
    elif menu == "📊 Power BI":
        show_powerbi_page()  # MỚI

def show_dashboard(df):
    import plotly.express as px
    
    st.title("Dashboard Tổng quan")
    
    if df.empty:
        st.warning("Chưa có dữ liệu. Vui lòng import hoặc thêm dữ liệu.")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng sinh viên", df['mssv'].nunique())
    with col2:
        st.metric("Điểm TB", f"{df['diem_tb'].mean():.2f}")
    with col3:
        st.metric("Cao nhất", f"{df['diem_tb'].max():.2f}")
    with col4:
        st.metric("Thấp nhất", f"{df['diem_tb'].min():.2f}")
    
    st.subheader("Thống kê theo học kỳ")
    col1, col2 = st.columns(2)
    with col1:
        sem1_count = len(df[df['semester'] == 1])
        st.metric("Học kỳ 1", f"{sem1_count} bản ghi")
    with col2:
        sem2_count = len(df[df['semester'] == 2])
        st.metric("Học kỳ 2", f"{sem2_count} bản ghi")
    
    st.subheader("Thống kê theo xếp loại")
    xep_loai_counts = df['xep_loai'].fillna('Chưa xếp loại').value_counts()
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(values=xep_loai_counts.values, names=xep_loai_counts.index, 
                    title='Phân bố xếp loại')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(x=xep_loai_counts.index, y=xep_loai_counts.values,
                    title='Số lượng theo xếp loại', labels={'x': 'Xếp loại', 'y': 'Số lượng'})
        st.plotly_chart(fig, use_container_width=True)
