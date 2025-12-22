import streamlit as st
import pandas as pd
import plotly.express as px
from config.subjects import SUBJECTS

def show_charts(df):
    st.title("📊 Biểu đồ phân tích")
    
    if df.empty:
        st.warning("Chưa có dữ liệu để phân tích.")
        return
    
    chart_class_avg(df)
    chart_xep_loai(df)
    chart_subject_avg(df)
    chart_semester_comparison(df)
    chart_distribution(df)

def chart_class_avg(df):
    st.subheader("📚 Điểm trung bình theo lớp")
    class_avg = df.groupby('class_name')['diem_tb'].mean().reset_index()
    fig = px.bar(
        class_avg, x='class_name', y='diem_tb', 
        title='Điểm TB theo lớp', color='diem_tb',
        labels={'class_name': 'Lớp', 'diem_tb': 'Điểm TB'},
        color_continuous_scale='viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

def chart_xep_loai(df):
    st.subheader("🎯 Phân bố xếp loại")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            df, names='xep_loai', 
            title='Tỷ lệ xếp loại học lực',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        xep_loai_counts = df['xep_loai'].value_counts().reset_index()
        xep_loai_counts.columns = ['Xếp loại', 'Số lượng']
        fig = px.bar(
            xep_loai_counts, x='Xếp loại', y='Số lượng',
            title='Số lượng theo xếp loại',
            color='Số lượng',
            color_continuous_scale='blues'
        )
        st.plotly_chart(fig, use_container_width=True)

def chart_subject_avg(df):
    st.subheader("📖 Điểm trung bình các môn học")
    
    subject_avg = []
    for key, info in SUBJECTS.items():
        if info['counts_gpa'] and key in df.columns:
            avg = pd.to_numeric(df[key], errors='coerce').mean()
            if pd.notna(avg):
                subject_avg.append({'Môn': info['name'], 'Điểm TB': float(avg)})
    
    if subject_avg:
        subject_df = pd.DataFrame(subject_avg)
        fig = px.line(
            subject_df, x='Môn', y='Điểm TB', 
            markers=True, title='Điểm TB các môn',
            line_shape='spline'
        )
        fig.update_traces(line_color='#667eea', marker_size=10)
        st.plotly_chart(fig, use_container_width=True)

def chart_semester_comparison(df):
    st.subheader("📅 So sánh theo học kỳ")
    
    semester_avg = df.groupby('semester')['diem_tb'].mean().reset_index()
    semester_avg['semester'] = semester_avg['semester'].map({1: 'Học kỳ 1', 2: 'Học kỳ 2'})
    
    fig = px.bar(
        semester_avg, x='semester', y='diem_tb', 
        title='Điểm TB theo học kỳ', 
        color='diem_tb',
        color_continuous_scale='purples'
    )
    st.plotly_chart(fig, use_container_width=True)

def chart_distribution(df):
    st.subheader("📉 Phân bố điểm trung bình")
    
    fig = px.histogram(
        df, x='diem_tb', nbins=20, 
        title='Phân bố điểm TB',
        color_discrete_sequence=['#667eea']
    )
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)
