# pages/manage_grades.py - Quản lý điểm sinh viên
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from config import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS
from database.grades_crud import delete_grade
from utils.calculations import calculate_grade

def manage_grades(conn, df):
    """Quản lý điểm sinh viên (sửa/xóa)"""
    st.title("Quản lý điểm sinh viên")
    
    # Bộ lọc tìm kiếm
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Tìm kiếm (MSSV hoặc Tên)")
    with col2:
        semester_filter = st.selectbox("Học kỳ", ['Tất cả', '1', '2'])
    with col3:
        xep_loai_filter = st.selectbox("Xếp loại", ['Tất cả'] + list(df['xep_loai'].dropna().unique()) if not df.empty else ['Tất cả'])
    
    # Áp dụng bộ lọc
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            filtered_df['mssv'].astype(str).str.contains(search, case=False, na=False) |
            filtered_df['student_name'].str.contains(search, case=False, na=False)
        ]
    if semester_filter != 'Tất cả':
        filtered_df = filtered_df[filtered_df['semester'] == int(semester_filter)]
    if xep_loai_filter != 'Tất cả':
        filtered_df = filtered_df[filtered_df['xep_loai'] == xep_loai_filter]
    
    # Hiển thị bảng điểm
    display_cols = ['id', 'mssv', 'student_name', 'class_name', 'semester', 'diem_tb', 'xep_loai']
    st.dataframe(filtered_df[display_cols], use_container_width=True)
    
    st.divider()
    
    # Tabs cho Sửa và Xóa
    tab1, tab2 = st.tabs(["Sửa điểm", "Xóa điểm"])
    
    with tab1:
        _render_edit_tab(conn, df, filtered_df)
    
    with tab2:
        _render_delete_tab(conn, df, filtered_df)

def _render_edit_tab(conn, df, filtered_df):
    """Render tab sửa điểm"""
    st.subheader("Sửa điểm sinh viên")
    if filtered_df.empty:
        st.warning("Không có dữ liệu để sửa.")
        return
    
    selected_id = st.selectbox("Chọn ID bản ghi cần sửa", filtered_df['id'].tolist(), key="edit_select")
    selected_row = df[df['id'] == selected_id].iloc[0]
    
    semester = int(selected_row.get('semester', 1))
    st.info(f"Đang sửa: **{selected_row['student_name']}** - MSSV: **{selected_row['mssv']}** - Học kỳ: **{semester}**")
    
    # Form sửa thông tin cơ bản
    col1, col2, col3 = st.columns(3)
    with col1:
        new_mssv = st.text_input("MSSV", value=selected_row['mssv'], key="edit_mssv")
    with col2:
        new_name = st.text_input("Họ tên", value=selected_row['student_name'], key="edit_name")
    with col3:
        new_class = st.text_input("Lớp", value=selected_row['class_name'] or '', key="edit_class")
    
    # Form sửa điểm
    st.write("**Điểm các môn:**")
    current_subjects = SEMESTER_1_SUBJECTS if semester == 1 else SEMESTER_2_SUBJECTS
    
    new_scores = {}
    cols = st.columns(5)
    for i, key in enumerate(current_subjects):
        with cols[i % 5]:
            current_score = selected_row.get(key)
            current_val = float(current_score) if pd.notna(current_score) else 0.0
            new_scores[key] = st.number_input(
                SUBJECTS[key]['name'], 
                0.0, 10.0, current_val, 
                key=f"edit_{key}"
            )
    
    if st.button("Lưu thay đổi", type="primary"):
        # Tính lại điểm TB
        scores_for_avg = {k: v for k, v in new_scores.items() 
                       if SUBJECTS[k]['counts_gpa'] and v > 0}
        new_diem_tb = round(np.mean(list(scores_for_avg.values())), 2) if scores_for_avg else 0.0
        new_xep_loai = calculate_grade(new_diem_tb)
        
        # Update database
        c = conn.cursor()
        update_fields = []
        update_values = []
        
        update_fields.append("mssv = ?")
        update_values.append(new_mssv)
        update_fields.append("student_name = ?")
        update_values.append(new_name)
        update_fields.append("class_name = ?")
        update_values.append(new_class)
        
        for key in current_subjects:
            update_fields.append(f"{key} = ?")
            update_values.append(float(new_scores[key]) if new_scores[key] > 0 else None)
        
        update_fields.append("diem_tb = ?")
        update_values.append(new_diem_tb)
        update_fields.append("xep_loai = ?")
        update_values.append(new_xep_loai)
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now())
        
        update_values.append(selected_id)
        
        query = f"UPDATE grades SET {', '.join(update_fields)} WHERE id = ?"
        c.execute(query, update_values)
        conn.commit()
        
        st.success(f"Đã cập nhật điểm cho {new_name} - ĐTB: {new_diem_tb} - Xếp loại: {new_xep_loai}")
        st.rerun()

def _render_delete_tab(conn, df, filtered_df):
    """Render tab xóa điểm"""
    st.subheader("Xóa điểm sinh viên")
    if filtered_df.empty:
        st.warning("Không có dữ liệu để xóa.")
        return
    
    # Chọn sinh viên để xóa
    delete_options = []
    for _, row in filtered_df.iterrows():
        label = f"ID: {row['id']} - {row['mssv']} - {row['student_name']} - HK{int(row['semester'])}"
        delete_options.append((row['id'], label))
    
    selected_delete = st.selectbox(
        "Chọn bản ghi cần xóa", 
        options=[opt[0] for opt in delete_options],
        format_func=lambda x: next(opt[1] for opt in delete_options if opt[0] == x),
        key="delete_select"
    )
    
    # Hiển thị thông tin chi tiết trước khi xóa
    delete_row = df[df['id'] == selected_delete].iloc[0]
    st.warning(f"""
    **Bạn sắp xóa:**
    - MSSV: {delete_row['mssv']}
    - Họ tên: {delete_row['student_name']}
    - Lớp: {delete_row['class_name']}
    - Học kỳ: {int(delete_row['semester'])}
    - Điểm TB: {delete_row['diem_tb']}
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        confirm = st.checkbox("Tôi xác nhận muốn xóa bản ghi này")
    with col2:
        if st.button("Xóa", type="primary", disabled=not confirm):
            delete_grade(conn, selected_delete)
            st.success(f"Đã xóa bản ghi của {delete_row['student_name']}!")
            st.rerun()
    
    st.divider()
    
    # Xóa nhiều bản ghi
    st.subheader("Xóa nhiều bản ghi")
    if st.checkbox("Hiển thị tùy chọn xóa hàng loạt"):
        multi_delete_ids = st.multiselect(
            "Chọn các bản ghi cần xóa",
            options=[opt[0] for opt in delete_options],
            format_func=lambda x: next(opt[1] for opt in delete_options if opt[0] == x)
        )
        
        if multi_delete_ids:
            st.error(f"Bạn đã chọn {len(multi_delete_ids)} bản ghi để xóa!")
            confirm_multi = st.checkbox("Tôi xác nhận muốn xóa TẤT CẢ các bản ghi đã chọn")
            
            if st.button("Xóa tất cả đã chọn", disabled=not confirm_multi):
                c = conn.cursor()
                for del_id in multi_delete_ids:
                    c.execute("DELETE FROM grades WHERE id = ?", (del_id,))
                conn.commit()
                st.success(f"Đã xóa {len(multi_delete_ids)} bản ghi!")
                st.rerun()