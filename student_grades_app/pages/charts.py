
# pages/charts.py - Biểu đồ phân tích
import streamlit as st
import pandas as pd
import plotly.express as px
from config import SUBJECTS

def show_charts(df):
    """Trang biểu đồ phân tích"""
    st.title("Biểu đồ phân tích")
    
    if df.empty:
        st.warning("Chưa có dữ liệu để phân tích.")
        return
    
    # Biểu đồ 1: Điểm TB theo lớp
    st.subheader("Điểm trung bình theo lớp")
    class_avg = df.groupby('class_name')['diem_tb'].mean().reset_index()
    fig1 = px.bar(class_avg, x='class_name', y='diem_tb', 
                  title='Điểm TB theo lớp', color='diem_tb',
                  labels={'class_name': 'Lớp', 'diem_tb': 'Điểm TB'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Biểu đồ 2: Phân bố xếp loại
    st.subheader("Phân bố xếp loại")
    fig2 = px.pie(df, names='xep_loai', title='Tỷ lệ xếp loại học lực')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Biểu đồ 3: Điểm TB các môn
    st.subheader("Điểm trung bình các môn học")
    subject_avg = []
    for key, info in SUBJECTS.items():
        if info['counts_gpa'] and key in df.columns:
            avg = pd.to_numeric(df[key], errors='coerce').mean()
            if pd.notna(avg):
                subject_avg.append({'Môn': info['name'], 'Điểm TB': float(avg)})
    
    if subject_avg:
        subject_df = pd.DataFrame(subject_avg)
        fig3 = px.line(subject_df, x='Môn', y='Điểm TB', markers=True, title='Điểm TB các môn')
        st.plotly_chart(fig3, use_container_width=True)
    
    # Biểu đồ 4: So sánh theo học kỳ
    st.subheader("So sánh theo học kỳ")
    semester_avg = df.groupby('semester')['diem_tb'].mean().reset_index()
    semester_avg['semester'] = semester_avg['semester'].map({1: 'Học kỳ 1', 2: 'Học kỳ 2'})
    fig4 = px.bar(semester_avg, x='semester', y='diem_tb', 
                  title='Điểm TB theo học kỳ', color='diem_tb')
    st.plotly_chart(fig4, use_container_width=True)
    
    # Biểu đồ 5: Phân bố điểm TB
    st.subheader("Phân bố điểm trung bình")
    fig5 = px.histogram(df, x='diem_tb', nbins=20, title='Phân bố điểm TB')
    st.plotly_chart(fig5, use_container_width=True)
