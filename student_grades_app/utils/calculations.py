# utils/calculations.py - Tính điểm TB và xếp loại
import pandas as pd
import numpy as np
from config import SUBJECTS

def calculate_grade(score):
    """Xếp loại học lực dựa trên điểm"""
    try:
        s = float(score)
    except Exception:
        s = 0.0
    
    if s >= 9.5: return 'Xuất sắc'
    elif s >= 8.5: return 'Giỏi'
    elif s >= 7.0: return 'Khá'
    elif s >= 5.5: return 'Trung bình'
    elif s >= 4.0: return 'Yếu'
    else: return 'Kém'

def calculate_average(row):
    """Tính điểm TB (không tính GDTC). Xử lý an toàn với giá trị non-numeric/NaN."""
    scores = []
    for key, info in SUBJECTS.items():
        if info['counts_gpa']:
            val = row.get(key)
            try:
                num = float(val) if pd.notna(val) else np.nan
            except Exception:
                num = np.nan
            if pd.notna(num) and num >= 0:
                scores.append(num)
    return round(float(np.mean(scores)), 2) if scores else 0.0
