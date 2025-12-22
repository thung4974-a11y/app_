import streamlit as st
import pandas as pd
import numpy as np
from config.subjects import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS, ACADEMIC_YEAR
from database.grades import save_grade, delete_grade, delete_grades_batch, can_take_semester_2
from utils.calculations import calculate_grade, calculate_average

def manage_grades(conn, df):
    st.title("📝 Quản lý điểm sinh viên")

    if df.empty:
        st.warning("Chưa có dữ liệu điểm.")
        return

    semester_filter = st.radio(
        "Chọn học kỳ hiển thị",
        ['Tất cả từng kỳ', 'Học kỳ 1', 'Học kỳ 2', 'Tổng hợp'],
        horizontal=True
    )

    filtered_df = filter_grades(df, semester_filter)
    display_grades_table(filtered_df, semester_filter)
    
    st.divider()
    search_and_delete(conn, df)

def filter_grades(df, semester_filter):
    if semester_filter == 'Học kỳ 1':
        return df[df['semester'] == 1].copy()
    elif semester_filter == 'Học kỳ 2':
        return df[df['semester'] == 2].copy()
    elif semester_filter == 'Tổng hợp':
        return create_combined_df(df)
    return df.copy()

def create_combined_df(df):
    combined_rows = []
    for mssv, group in df.groupby('mssv'):
        if set(group['semester']) == {1, 2}:
            sem1 = group[group['semester'] == 1].iloc[0]
            sem2 = group[group['semester'] == 2].iloc[0]
            dtb = round((sem1['diem_tb'] + sem2['diem_tb']) / 2, 2)
            combined_rows.append({
                'mssv': mssv,
                'student_name': sem1['student_name'],
                'class_name': sem1['class_name'],
                'diem_tb_hk1': sem1['diem_tb'],
                'diem_tb_hk2': sem2['diem_tb'],
                'diem_tb': dtb,
                'xep_loai': calculate_grade(dtb)
            })
    return pd.DataFrame(combined_rows)

def display_grades_table(filtered_df, semester_filter):
    if filtered_df.empty:
        st.info("Không có dữ liệu phù hợp.")
        return
    
    if semester_filter == 'Tổng hợp':
        display_df = filtered_df[['mssv', 'student_name', 'class_name', 'diem_tb_hk1', 'diem_tb_hk2', 'diem_tb', 'xep_loai']]
        display_df.columns = ['MSSV', 'Họ tên', 'Lớp', 'ĐTB HK1', 'ĐTB HK2', 'Điểm TB', 'Xếp loại']
    else:
        display_df = filtered_df[['mssv', 'student_name', 'class_name', 'semester', 'diem_tb', 'xep_loai']]
        display_df.columns = ['MSSV', 'Họ tên', 'Lớp', 'Học kỳ', 'Điểm TB', 'Xếp loại']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.caption(f"Tổng số: {len(display_df)} bản ghi")

def search_and_delete(conn, df):
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Tìm kiếm sinh viên (MSSV hoặc Tên)")
    with col2:
        show_delete = st.checkbox("Hiển thị chức năng Xóa", value=True)
    
    if search_term:
        search_results = df[
            df['mssv'].astype(str).str.contains(search_term, case=False, na=False) |
            df['student_name'].str.contains(search_term, case=False, na=False)
        ]
        if not search_results.empty:
            st.success(f"Tìm thấy {len(search_results)} bản ghi")
            st.dataframe(search_results[['mssv', 'student_name', 'class_name', 'semester', 'diem_tb', 'xep_loai']], 
                        use_container_width=True, hide_index=True)
        else:
            st.warning("Không tìm thấy sinh viên phù hợp.")
    
    if show_delete:
        delete_grades_ui(conn, df)

def delete_grades_ui(conn, df):
    st.divider()
    st.subheader("🗑️ Xóa điểm sinh viên")
    
    delete_options = {
        row['id']: f"{row['mssv']} - {row['student_name']} - HK{int(row['semester'])} - ĐTB {row['diem_tb']:.2f}"
        for _, row in df.iterrows()
    }
    
    delete_mode = st.radio("Chế độ xóa", ["Xóa 1", "Xóa nhiều"], horizontal=True)
    
    if delete_mode == "Xóa 1":
        del_id = st.selectbox("Chọn bản ghi", delete_options.keys(), format_func=lambda x: delete_options[x])
        if st.checkbox("Xác nhận xóa"):
            if st.button("🗑️ Xóa", type="primary"):
                delete_grade(conn, del_id)
                st.success("Đã xóa bản ghi!")
                st.rerun()
    else:
        del_ids = st.multiselect("Chọn các bản ghi", delete_options.keys(), format_func=lambda x: delete_options[x])
        if del_ids and st.checkbox("Xác nhận xóa tất cả"):
            if st.button("🗑️ Xóa tất cả", type="primary"):
                delete_grades_batch(conn, del_ids)
                st.success(f"Đã xóa {len(del_ids)} bản ghi!")
                st.rerun()

def add_grade_form(conn):
    st.title("➕ Thêm điểm sinh viên")
    
    semester = st.radio("Chọn học kỳ", [1, 2], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        mssv = st.text_input("MSSV *")
        student_name = st.text_input("Họ tên *")
        class_name = st.text_input("Lớp")
    
    can_sem2 = True
    if semester == 2 and mssv:
        can_sem2, message = can_take_semester_2(conn, mssv)
        st.success(message) if can_sem2 else st.error(message)
    
    st.subheader(f"📖 Điểm các môn - Học kỳ {semester}")
    current_subjects = SEMESTER_1_SUBJECTS if semester == 1 else SEMESTER_2_SUBJECTS
    
    subject_scores = {}
    cols = st.columns(3)
    for i, key in enumerate(current_subjects):
        info = SUBJECTS[key]
        with cols[i % 3]:
            label = info['name']
            if not info['counts_gpa']:
                label += " (Không tính GPA)"
            if info.get('mandatory'):
                label += " *"
            subject_scores[key] = st.number_input(label, 0.0, 10.0, 0.0, key=f"add_{key}")
    
    st.info(f"Năm học: **{ACADEMIC_YEAR}** (cố định)")
    
    if st.button("💾 Thêm điểm", type="primary", disabled=(semester == 2 and not can_sem2)):
        if mssv and student_name:
            scores_for_avg = {k: v for k, v in subject_scores.items() if SUBJECTS[k]['counts_gpa'] and v > 0}
            diem_tb = round(np.mean(list(scores_for_avg.values())), 2) if scores_for_avg else 0.0
            xep_loai = calculate_grade(diem_tb)
            
            all_scores = {k: None for k in SUBJECTS.keys()}
            all_scores.update(subject_scores)
            
            params = (
                mssv, student_name, class_name, int(semester),
                float(all_scores['triet']) if all_scores['triet'] else None,
                float(all_scores['giai_tich_1']) if all_scores['giai_tich_1'] else None,
                float(all_scores['giai_tich_2']) if all_scores['giai_tich_2'] else None,
                float(all_scores['tieng_an_do_1']) if all_scores['tieng_an_do_1'] else None,
                float(all_scores['tieng_an_do_2']) if all_scores['tieng_an_do_2'] else None,
                float(all_scores['gdtc']) if all_scores['gdtc'] else None,
                float(all_scores['thvp']) if all_scores['thvp'] else None,
                float(all_scores['tvth']) if all_scores['tvth'] else None,
                float(all_scores['phap_luat']) if all_scores['phap_luat'] else None,
                float(all_scores['logic']) if all_scores['logic'] else None,
                float(diem_tb), xep_loai, int(ACADEMIC_YEAR)
            )
            
            ok, err = save_grade(conn, params)
            if ok:
                st.success(f"Đã thêm điểm cho {student_name} - ĐTB: {diem_tb} - Xếp loại: {xep_loai}")
            else:
                st.error(f"Lỗi: {err}")
        else:
            st.error("Vui lòng nhập MSSV và Họ tên!")
