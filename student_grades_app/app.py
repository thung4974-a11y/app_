# app.py - File chính (Entry point)
import streamlit as st
from styles import PREMIUM_SIDEBAR
from database.connection import init_db
from pages.login import login_page
from dashboards.teacher import teacher_dashboard
from dashboards.student import student_dashboard

def main():
    """Hàm chính của ứng dụng"""
    st.set_page_config(
        page_title="Quản lý điểm sinh viên", 
        page_icon="logotl.jpg", 
        layout="wide"
    )
    
    # Áp dụng CSS sidebar
    st.markdown(PREMIUM_SIDEBAR, unsafe_allow_html=True)
    
    # Khởi tạo database
    conn = init_db()
    
    # Khởi tạo session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    # Điều hướng
    if not st.session_state['logged_in']:
        login_page(conn)
    else:
        if st.session_state['role'] == 'teacher':
            teacher_dashboard(conn)
        else:
            student_dashboard(conn)

if __name__ == "__main__":
    main()