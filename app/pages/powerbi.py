# pages/powerbi.py - Power BI Embed

import streamlit as st
import streamlit.components.v1 as components

# ======================== CẤU HÌNH POWER BI ========================
# Thay thế bằng URL embed thực tế từ Power BI Service
POWERBI_REPORTS = {
    'tong_quan': {
        'name': 'Báo cáo Tổng quan',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID_1&autoAuth=true&ctid=YOUR_TENANT_ID',
        'description': 'Tổng quan về kết quả học tập toàn trường'
    },
    'theo_lop': {
        'name': 'Phân tích theo Lớp',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID_2&autoAuth=true&ctid=YOUR_TENANT_ID',
        'description': 'So sánh kết quả học tập giữa các lớp'
    },
    'theo_mon': {
        'name': 'Phân tích theo Môn học',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID_3&autoAuth=true&ctid=YOUR_TENANT_ID',
        'description': 'Phân tích chi tiết từng môn học'
    },
    'xu_huong': {
        'name': 'Xu hướng theo thời gian',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=YOUR_REPORT_ID_4&autoAuth=true&ctid=YOUR_TENANT_ID',
        'description': 'Theo dõi xu hướng điểm qua các kỳ'
    }
}

def show_powerbi_page():
    """Trang hiển thị Power BI Reports"""
    st.title("📊 Báo cáo Power BI")
    
    st.markdown("""
    <style>
    .powerbi-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .report-card {
        background: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs cho các loại báo cáo
    tab1, tab2, tab3 = st.tabs(["📈 Xem báo cáo", "⚙️ Cấu hình", "📖 Hướng dẫn"])
    
    with tab1:
        show_reports_tab()
    
    with tab2:
        show_config_tab()
    
    with tab3:
        show_guide_tab()

def show_reports_tab():
    """Tab hiển thị các báo cáo Power BI"""
    st.subheader("Chọn báo cáo để xem")
    
    # Dropdown chọn báo cáo
    report_options = {v['name']: k for k, v in POWERBI_REPORTS.items()}
    selected_report_name = st.selectbox(
        "Báo cáo",
        options=list(report_options.keys()),
        format_func=lambda x: f"📊 {x}"
    )
    
    if selected_report_name:
        report_key = report_options[selected_report_name]
        report = POWERBI_REPORTS[report_key]
        
        # Hiển thị thông tin báo cáo
        st.info(f"**Mô tả:** {report['description']}")
        
        # Tùy chọn hiển thị
        col1, col2 = st.columns(2)
        with col1:
            height = st.slider("Chiều cao (px)", 400, 1000, 600, 50)
        with col2:
            show_nav = st.checkbox("Hiện thanh điều hướng", value=True)
        
        # Embed Power BI Report
        embed_powerbi_report(report['url'], height=height, show_nav=show_nav)
        
        # Nút mở trong tab mới
        st.markdown(f"""
        <a href="{report['url']}" target="_blank" style="
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            margin-top: 10px;
        ">🔗 Mở trong tab mới</a>
        """, unsafe_allow_html=True)

def embed_powerbi_report(embed_url, height=600, show_nav=True):
    """Embed Power BI report vào Streamlit"""
    
    # Kiểm tra URL hợp lệ
    if "YOUR_REPORT_ID" in embed_url:
        st.warning("⚠️ Vui lòng cấu hình URL Power BI thực tế trong file `pages/powerbi.py`")
        st.code("""
# Thay thế trong POWERBI_REPORTS:
'url': 'https://app.powerbi.com/reportEmbed?reportId=YOUR_REAL_REPORT_ID&autoAuth=true&ctid=YOUR_TENANT_ID'
        """)
        
        # Hiển thị demo placeholder
        st.markdown(f"""
        <div style="
            width: 100%;
            height: {height}px;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
        ">
            <div style="text-align: center;">
                <div style="font-size: 48px; margin-bottom: 20px;">📊</div>
                <div>Power BI Report sẽ hiển thị ở đây</div>
                <div style="font-size: 14px; color: #888; margin-top: 10px;">
                    Cần cấu hình URL embed thực tế
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Tạo iframe HTML
    nav_param = "" if show_nav else "&navContentPaneEnabled=false"
    
    iframe_html = f"""
    <iframe 
        title="Power BI Report"
        width="100%" 
        height="{height}" 
        src="{embed_url}{nav_param}"
        frameborder="0" 
        allowFullScreen="true"
        style="border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
    </iframe>
    """
    
    components.html(iframe_html, height=height + 20)

def show_config_tab():
    """Tab cấu hình Power BI"""
    st.subheader("⚙️ Cấu hình kết nối Power BI")
    
    st.markdown("""
    ### Cách lấy URL Embed từ Power BI Service:
    
    1. **Đăng nhập** vào [Power BI Service](https://app.powerbi.com)
    2. **Mở báo cáo** bạn muốn embed
    3. Click **File → Embed report → Website or portal**
    4. **Copy URL** từ hộp thoại
    5. **Dán URL** vào cấu hình bên dưới
    """)
    
    st.divider()
    
    # Form thêm báo cáo mới
    st.subheader("Thêm báo cáo mới")
    
    with st.form("add_report_form"):
        col1, col2 = st.columns(2)
        with col1:
            report_name = st.text_input("Tên báo cáo")
        with col2:
            report_key = st.text_input("Key (không dấu, không khoảng trắng)")
        
        report_url = st.text_input("URL Embed", placeholder="https://app.powerbi.com/reportEmbed?reportId=...")
        report_desc = st.text_area("Mô tả", max_chars=200)
        
        submitted = st.form_submit_button("Thêm báo cáo", type="primary")
        
        if submitted:
            if report_name and report_key and report_url:
                # Trong thực tế, bạn sẽ lưu vào database hoặc file config
                st.success(f"✅ Đã thêm báo cáo: {report_name}")
                st.info("💡 Để lưu vĩnh viễn, hãy thêm vào POWERBI_REPORTS trong file powerbi.py")
                st.code(f"""
'{report_key}': {{
    'name': '{report_name}',
    'url': '{report_url}',
    'description': '{report_desc}'
}}
                """)
            else:
                st.error("Vui lòng điền đầy đủ thông tin!")
    
    st.divider()
    
    # Hiển thị cấu hình hiện tại
    st.subheader("Cấu hình hiện tại")
    for key, report in POWERBI_REPORTS.items():
        with st.expander(f"📊 {report['name']} ({key})"):
            st.write(f"**Mô tả:** {report['description']}")
            st.code(report['url'], language=None)

def show_guide_tab():
    """Tab hướng dẫn sử dụng"""
    st.subheader("📖 Hướng dẫn tích hợp Power BI")
    
    st.markdown("""
    ## Yêu cầu
    
    - **Power BI Pro** hoặc **Premium Per User** license
    - Báo cáo đã được publish lên Power BI Service
    - Quyền **Embed** được bật cho báo cáo
    
    ---
    
    ## Các bước tích hợp
    
    ### 1. Chuẩn bị báo cáo Power BI
    
    ```
    1. Mở Power BI Desktop
    2. Tạo hoặc mở báo cáo
    3. Kết nối với nguồn dữ liệu (có thể dùng SQLite database)
    4. Publish lên Power BI Service
    ```
    
    ### 2. Lấy URL Embed
    
    ```
    1. Đăng nhập Power BI Service (app.powerbi.com)
    2. Mở báo cáo → File → Embed report → Website or portal
    3. Copy URL embed
    ```
    
    ### 3. Cấu hình trong Streamlit
    
    ```python
    # Thêm vào POWERBI_REPORTS trong pages/powerbi.py
    'my_report': {
        'name': 'Tên báo cáo',
        'url': 'URL_EMBED_CỦA_BẠN',
        'description': 'Mô tả báo cáo'
    }
    ```
    
    ---
    
    ## Kết nối Power BI với SQLite
    
    Để Power BI đọc dữ liệu từ SQLite database:
    
    ```
    1. Trong Power BI Desktop → Get Data → More
    2. Chọn ODBC hoặc sử dụng Python script
    3. Kết nối tới file student_grades.db
    ```
    
    **Hoặc sử dụng Python script trong Power BI:**
    
    ```python
    import pandas as pd
    import sqlite3
    
    conn = sqlite3.connect('path/to/student_grades.db')
    df = pd.read_sql_query("SELECT * FROM grades", conn)
    conn.close()
    ```
    
    ---
    
    ## Bảo mật
    
    ⚠️ **Lưu ý quan trọng:**
    
    - Không chia sẻ URL embed công khai nếu chứa dữ liệu nhạy cảm
    - Sử dụng Row-Level Security (RLS) trong Power BI để giới hạn quyền xem
    - Cân nhắc sử dụng Power BI Embedded API cho bảo mật cao hơn
    """)

def embed_powerbi_with_api(report_id, group_id, access_token):
    """
    Embed Power BI với API (bảo mật hơn)
    Yêu cầu: Azure AD App Registration
    """
    embed_url = f"https://app.powerbi.com/reportEmbed?reportId={report_id}&groupId={group_id}"
    
    iframe_html = f"""
    <iframe 
        title="Power BI Report"
        width="100%" 
        height="600" 
        src="{embed_url}"
        frameborder="0" 
        allowFullScreen="true">
    </iframe>
    <script src="https://cdn.powerbi.com/powerbi-client/v2.20.3/powerbi.min.js"></script>
    <script>
        var embedConfig = {{
            type: 'report',
            id: '{report_id}',
            embedUrl: '{embed_url}',
            accessToken: '{access_token}',
            settings: {{
                navContentPaneEnabled: true,
                filterPaneEnabled: true
            }}
        }};
        var reportContainer = document.getElementById('reportContainer');
        var report = powerbi.embed(reportContainer, embedConfig);
    </script>
    """
    
    components.html(iframe_html, height=620)
