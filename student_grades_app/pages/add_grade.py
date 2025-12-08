# pages/add_grade.py - Thêm điểm sinh viên
import streamlit as st
import numpy as np
from config import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS, ACADEMIC_YEAR
from database.grades_crud import save_grade
from utils.calculations import calculate_grade
from utils.validators import can_take_semester_2

def add_grade_form(conn):
    """Form thêm điểm sinh viên mới"""
    st.title("Thêm điểm sinh viên")
    
    semester = st.radio("Chọn học kỳ", [1, 2], horizontal=True)
    
    col1, col2 = st.columns(2)
    with col1:
        mssv = st.text_input("MSSV *")
        student_name = st.text_input("Họ tên *")
        class_name = st.text_input("Lớp")
    
    # Kiểm tra điều kiện học kỳ 2
    can_sem2 = True
    if semester == 2 and mssv:
        can_sem2, message = can_take_semester_2(conn, mssv)
        if can_sem2:
            st.success(f"{message}")
        else:
            st.error(f"{message}")
    
    st.subheader(f"Điểm các môn - Học kỳ {semester}")
    
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
    
    if st.button("Thêm điểm", type="primary", disabled=(semester == 2 and not can_sem2)):
        if mssv and student_name:
            scores_for_avg = {k: v for k, v in subject_scores.items() 
                           if SUBJECTS[k]['counts_gpa'] and v > 0}
            diem_tb = round(np.mean(list(scores_for_avg.values())), 2) if scores_for_avg else 0.0
            xep_loai = calculate_grade(diem_tb)
            
            all_scores = {k: None for k in SUBJECTS.keys()}
            all_scores.update(subject_scores)
            
            params = (
                mssv, student_name, class_name, int(semester),
                float(all_scores['triet']) if all_scores['triet'] is not None else None,
                float(all_scores['giai_tich_1']) if all_scores['giai_tich_1'] is not None else None,
                float(all_scores['giai_tich_2']) if all_scores['giai_tich_2'] is not None else None,
                float(all_scores['tieng_an_do_1']) if all_scores['tieng_an_do_1'] is not None else None,
                float(all_scores['tieng_an_do_2']) if all_scores['tieng_an_do_2'] is not None else None,
                float(all_scores['gdtc']) if all_scores['gdtc'] is not None else None,
                float(all_scores['thvp']) if all_scores['thvp'] is not None else None,
                float(all_scores['tvth']) if all_scores['tvth'] is not None else None,
                float(all_scores['phap_luat']) if all_scores['phap_luat'] is not None else None,
                float(all_scores['logic']) if all_scores['logic'] is not None else None,
                float(diem_tb), xep_loai, int(ACADEMIC_YEAR)
            )
            ok, err = save_grade(conn, params)
            if ok:
                st.success(f"Đã thêm điểm cho {student_name} - ĐTB: {diem_tb} - Xếp loại: {xep_loai}")
            else:
                st.error(f"Lỗi khi lưu vào DB: {err}")
        else:
            st.error("Vui lòng nhập MSSV và Họ tên!")