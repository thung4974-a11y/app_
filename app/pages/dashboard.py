import streamlit as st
import plotly.express as px

def show_dashboard(df):
    st.title("📊 Dashboard Tổng quan")
    
    if df.empty:
        st.warning("Chưa có dữ liệu. Vui lòng import hoặc thêm dữ liệu.")
        return
    
    # Metrics chính
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Tổng sinh viên", df['mssv'].nunique())
    with col2:
        st.metric("📈 Điểm TB", f"{df['diem_tb'].mean():.2f}")
    with col3:
        st.metric("🔝 Cao nhất", f"{df['diem_tb'].max():.2f}")
    with col4:
        st.metric("🔻 Thấp nhất", f"{df['diem_tb'].min():.2f}")
    
    # Thống kê theo học kỳ
    st.subheader("📅 Thống kê theo học kỳ")
    col1, col2 = st.columns(2)
    with col1:
        sem1_count = len(df[df['semester'] == 1])
        st.metric("Học kỳ 1", f"{sem1_count} bản ghi")
    with col2:
        sem2_count = len(df[df['semester'] == 2])
        st.metric("Học kỳ 2", f"{sem2_count} bản ghi")
    
    # Biểu đồ xếp loại
    st.subheader("🎯 Thống kê theo xếp loại")
    xep_loai_counts = df['xep_loai'].fillna('Chưa xếp loại').value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            values=xep_loai_counts.values, 
            names=xep_loai_counts.index, 
            title='Phân bố xếp loại'
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(
            x=xep_loai_counts.index, 
            y=xep_loai_counts.values,
            title='Số lượng theo xếp loại', 
            labels={'x': 'Xếp loại', 'y': 'Số lượng'}
        )
        st.plotly_chart(fig, use_container_width=True)
