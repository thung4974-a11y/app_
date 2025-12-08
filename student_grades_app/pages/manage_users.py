# pages/manage_users.py - Quản lý tài khoản
import streamlit as st
from database.users_crud import create_user, get_all_users, delete_user

def manage_users(conn):
    """Trang quản lý tài khoản"""
    st.title("Quản lý tài khoản")
    
    tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])
    
    with tab1:
        users_df = get_all_users(conn)
        st.dataframe(users_df, use_container_width=True)
        
        if len(users_df) > 1:
            user_to_delete = st.selectbox("Chọn user để xóa", 
                                          users_df[users_df['username'] != 'admin']['id'].tolist())
            if st.button("Xóa user"):
                delete_user(conn, user_to_delete)
                st.success("Đã xóa!")
                st.rerun()
    
    with tab2:
        st.subheader("Thêm tài khoản mới")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        new_fullname = st.text_input("Họ tên")
        new_role = st.selectbox("Vai trò", ["student", "teacher"])
        new_student_id = st.text_input("MSSV (nếu là học sinh)") if new_role == "student" else None
        
        if st.button("Tạo tài khoản"):
            if new_username and new_password and new_fullname:
                if create_user(conn, new_username, new_password, new_fullname, new_role, new_student_id):
                    st.success("Đã tạo tài khoản!")
                    st.rerun()
                else:
                    st.error("Username đã tồn tại!")
            else:
                st.error("Vui lòng điền đầy đủ thông tin!")