# dashboards/teacher.py - Dashboard giáo viên
import streamlit as st
from database.grades_crud import load_grades
from pages import (
    show_dashboard,
    manage_grades,
    show_ranking,
    add_grade_form,
    import_data,
    export_data,
    clean_data_page,
    manage_users,
    show_charts
)

def teacher_dashboard(conn):
    """Dashboard cho giáo viên"""
    st.sidebar.title(f"{st.session_state.get('fullname','')}")
    st.sidebar.write("Vai trò: **Giáo viên**")
    
    if st.sidebar.button("Đăng xuất"):
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
        "Biểu đồ phân tích"
    ])
    
    df = load_grades(conn)
    
    if menu == "Dashboard":
        show_dashboard(df)
    elif menu == "Quản lý điểm":
        manage_grades(conn, df)
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