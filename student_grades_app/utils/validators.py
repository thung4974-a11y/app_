# utils/validators.py - Kiểm tra điều kiện
from database.grades_crud import load_grades

def can_take_semester_2(conn, mssv):
    """Kiểm tra điều kiện học kỳ 2: TB Giải tích 1 + Tiếng Ấn Độ 1 >= 4"""
    df = load_grades(conn)
    student_sem1 = df[(df['mssv'] == mssv) & (df['semester'] == 1)]
    
    if student_sem1.empty:
        return False, "Chưa có điểm học kỳ 1"
    
    row = student_sem1.iloc[0]
    try:
        giai_tich_1 = float(row.get('giai_tich_1') or 0)
    except Exception:
        giai_tich_1 = 0
    try:
        tieng_an_do_1 = float(row.get('tieng_an_do_1') or 0)
    except Exception:
        tieng_an_do_1 = 0
    avg = (giai_tich_1 + tieng_an_do_1) / 2.0
    
    if avg >= 4:
        return True, f"Đủ điều kiện (TB: {avg:.2f})"
    else:
        return False, f"Chưa đủ điều kiện (TB: {avg:.2f} < 4)"