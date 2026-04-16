"""
AI 智能客服系统 - 主入口
"""
import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(
    page_title="AI 智能客服系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    /* 隐藏顶部导航栏的默认样式 */
    [data-testid="stSidebarNav"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 0 12px 0;
        padding-top: 20px;
    }
    
    [data-testid="stSidebarNav"] button {
        color: white !important;
        font-weight: 500;
        padding: 12px 20px;
        margin: 4px 8px;
        border-radius: 8px;
        transition: all 0.2s;
    }
    
    [data-testid="stSidebarNav"] button:hover {
        background: rgba(255,255,255,0.2);
    }
    
    [data-testid="stSidebarNav"] [aria-current="page"] {
        background: rgba(255,255,255,0.25) !important;
        font-weight: 700;
    }
    
    /* 侧边栏底部信息 */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 300px;
        padding: 16px;
        background: rgba(0,0,0,0.1);
        color: white;
        font-size: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# 初始化数据库
from database import init_db, get_dashboard_stats
init_db()

# ==================== 首页内容 ====================
st.markdown("""
<div style="text-align:center;padding:40px 0 20px">
    <span style="font-size:4em">🤖</span>
    <h1 style="font-size:2.2em;background:linear-gradient(90deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:8px 0">
        AI 智能客服系统
    </h1>
    <p style="color:#94a3b8;font-size:1.1em">基于 RAG 的企业级智能客服解决方案</p>
</div>
""", unsafe_allow_html=True)

# 功能概览卡片
col1, col2, col3, col4 = st.columns(4)
cards = [
    ("💬", "智能客服", "基于知识库的 AI 自动问答", "#667eea"),
    ("📊", "数据看板", "对话量、满意度、趋势分析", "#f093fb"),
    ("📋", "对话记录", "查看所有对话详情与状态", "#4facfe"),
    ("📚", "知识库管理", "上传文档、管理 FAQ 知识", "#43e97b"),
]
for col, (icon, title, desc, color) in zip([col1, col2, col3, col4], cards):
    with col:
        st.markdown(f"""
        <div style="background:white;border:1px solid #e2e8f0;border-radius:12px;padding:24px;
                    text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.06);transition:transform 0.2s">
            <div style="font-size:2.2em;margin-bottom:8px">{icon}</div>
            <div style="font-weight:600;color:#1e293b;margin-bottom:4px">{title}</div>
            <div style="font-size:0.85em;color:#64748b">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 快速统计
stats = get_dashboard_stats()
st.subheader("📈 系统概览")
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("总对话数", stats["total_convs"])
with s2:
    st.metric("总提问数", stats["total_questions"])
with s3:
    st.metric("平均满意度", f"{stats['avg_rating']} / 5")
with s4:
    st.metric("知识库文档", stats["doc_count"])

st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#94a3b8;font-size:0.85em;padding:20px 0">
    技术栈：DeepSeek API · ChromaDB · Streamlit · SQLite · matplotlib<br>
    <span style="color:#cbd5e1">Built with ❤️</span>
</div>
""", unsafe_allow_html=True)
