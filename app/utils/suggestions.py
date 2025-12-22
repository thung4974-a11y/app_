# utils/suggestions.py - Gợi ý học tập

import streamlit as st
import pandas as pd
from config.subjects import SUBJECTS, SEMESTER_1_SUBJECTS, SEMESTER_2_SUBJECTS, NEXT_SUBJECTS

def generate_study_suggestions(row, semester):
    """Tạo gợi ý học tập dựa trên điểm số"""
    suggestions = {
        'hoc_lai': [],
        'cai_thien': [],
        'can_hoc': [],
        'hoc_tiep': []
    }
    
    current_subjects = SEMESTER_1_SUBJECTS if semester == 1 else SEMESTER_2_SUBJECTS
    
    for key in current_subjects:
        info = SUBJECTS[key]
        score = row.get(key)
        
        try:
            score_val = float(score) if pd.notna(score) else None
        except:
            score_val = None
        
        if score_val is None:
            suggestions['can_hoc'].append(info['name'])
        elif score_val < 4:
            suggestions['hoc_lai'].append(f"{info['name']} ({score_val:.1f})")
        elif score_val < 6:
            suggestions['cai_thien'].append(f"{info['name']} ({score_val:.1f})")
        
        if score_val is not None and score_val >= 4 and key in NEXT_SUBJECTS:
            next_subject = NEXT_SUBJECTS[key]
            if semester == 1:
                next_name = {
                    'phap_luat': 'Pháp luật',
                    'giai_tich_2': 'Giải tích 2',
                    'tieng_an_do_2': 'Tiếng Ấn Độ 2'
                }.get(next_subject, next_subject)
            else:
                next_name = {
                    'tu_tuong': 'Tư tưởng (Năm 2)',
                    'giai_tich_3': 'Giải tích 3 (Năm 2)',
                    'tieng_an_do_3': 'Tiếng Ấn Độ 3 (Năm 2)'
                }.get(next_subject, next_subject)
            suggestions['hoc_tiep'].append(f"{next_name}")
    
    return suggestions

def display_study_suggestions(suggestions, semester):
    """Hiển thị gợi ý học tập"""
    st.markdown(f"### Gợi ý học tập - Học kỳ {semester}")
    
    has_suggestions = False
    
    if suggestions['hoc_lai']:
        has_suggestions = True
        st.error(f"**🔴 Cần học lại (điểm < 4):** {', '.join(suggestions['hoc_lai'])}")
    
    if suggestions['cai_thien']:
        has_suggestions = True
        st.warning(f"**🟡 Nên cải thiện (điểm 4-6):** {', '.join(suggestions['cai_thien'])}")
    
    if suggestions['can_hoc']:
        has_suggestions = True
        st.info(f"**🔵 Cần phải học (chưa có điểm):** {', '.join(suggestions['can_hoc'])}")
    
    if suggestions['hoc_tiep']:
        has_suggestions = True
        st.success(f"**🟢 Đủ điều kiện học tiếp:** {', '.join(suggestions['hoc_tiep'])}")
    
    if not has_suggestions:
        st.success("Bạn đã hoàn thành tốt học kỳ này!")
