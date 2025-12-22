import streamlit as st
from database.users import get_all_users, create_user, delete_user

def manage_users(conn):
    st.title("👥 Quản lý tài khoản")
    
    tab_list, tab_create = st.tabs(["📋 Danh sách", "➕ Thêm mới"])
    
    with tab_list:
        users_df = get_all_users(conn)
        st.dataframe(users_df, use_container_width=True)
        
        deletable = users_df[users_df["username"] != "admin"]
        
        if not deletable.empty:
            user_id = st.selectbox("Chọn user để xóa", deletable["id"].tolist())
            
            if st.button("🗑️ Xóa user", type="primary"):
                delete_user(conn, user_id)
                st.success("Đã xóa tài khoản!")
                st.rerun()
    
    with tab_create:
        st.subheader("➕ Thêm tài khoản mới")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        fullname = st.text_input("Họ tên")
        role = st.selectbox("Vai trò", ["student", "teacher"])
        
        student_id = st.text_input("MSSV") if role == "student" else None
        
        if st.button("💾 Tạo tài khoản", type="primary"):
            if not username or not password or not fullname:
                st.error("Vui lòng điền đầy đủ thông tin!")
                return
            
            if create_user(conn, username, password, fullname, role, student_id):
                st.success("Tạo tài khoản thành công!")
                st.rerun()
            else:
                st.error("Username đã tồn tại!")
