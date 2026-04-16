"""
AI 智能客服系统 - 用户聊天页面
"""
import streamlit as st
import uuid
from datetime import datetime
from database import (
    init_db, get_or_create_user, create_conversation, add_message,
    get_conversation_messages, get_active_conversation,
    end_conversation, add_rating, has_rating, mark_handover
)
init_db()
from ai_engine import get_ai_engine


def init_chat_state():
    """初始化聊天相关 session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "show_rating" not in st.session_state:
        st.session_state.show_rating = False


def render_chat_message(role, content, sources=None, timestamp=None):
    """渲染单条聊天消息"""
    if role == "user":
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin:8px 0">
            <div style="background:linear-gradient(135deg,#667eea,#764ba2);color:white;
                        padding:12px 18px;border-radius:18px 18px 4px 18px;
                        max-width:75%;font-size:0.95em;line-height:1.6;
                        box-shadow:0 2px 8px rgba(102,126,234,0.3)">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        source_html = ""
        if sources:
            source_items = "".join([
                f'<div style="background:rgba(102,126,234,0.08);padding:6px 10px;'
                f'border-radius:6px;font-size:0.82em;margin-top:4px;'
                f'border-left:3px solid #667eea">'
                f'📖 来源 {i+1}（相关度 {s["relevance"]}）<br>{s["content"][:100]}...'
                f'</div>'
                for i, s in enumerate(sources[:2])
            ])
            source_html = f'<div style="margin-top:6px">{source_items}</div>'

        st.markdown(f"""
        <div style="display:flex;justify-content:flex-start;margin:8px 0">
            <div style="background:#f8f9fc;color:#2d3748;
                        padding:12px 18px;border-radius:18px 18px 18px 4px;
                        max-width:75%;font-size:0.95em;line-height:1.6;
                        border:1px solid #e2e8f0;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
                <div style="font-weight:500;color:#667eea;margin-bottom:4px;font-size:0.85em">🤖 AI 客服</div>
                <div style="white-space:pre-wrap">{content}</div>
                {source_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    st.title("💬 智能客服")

    init_chat_state()

    # 获取或创建用户
    user = get_or_create_user(st.session_state.session_id)

    # 侧边栏
    with st.sidebar:
        st.markdown("---")
        st.subheader("👤 用户设置")

        user_name = st.text_input("你的昵称", value=user["name"], key="user_name_input")
        if user_name and user_name != user["name"]:
            get_or_create_user(st.session_state.session_id, user_name)
            st.success("昵称已更新！")
            st.rerun()

        st.markdown("---")
        st.subheader("⚙️ 对话控制")

        if st.button("🆕 开始新对话", use_container_width=True):
            if st.session_state.current_conv_id:
                end_conversation(st.session_state.current_conv_id)
            st.session_state.current_conv_id = None
            st.session_state.chat_history = []
            st.session_state.show_rating = False
            st.rerun()

        if st.button("🔄 转接人工客服", use_container_width=True):
            if st.session_state.current_conv_id:
                mark_handover(st.session_state.current_conv_id)
                st.warning("已标记转接人工，客服人员将尽快为您服务！")

        st.markdown("---")
        st.caption(f"会话ID：{st.session_state.session_id}")

        kb_stats = get_ai_engine().get_kb_stats()
        st.caption(f"📚 知识库条目：{kb_stats['total_chunks']} 条")

    # 主动画区域
    chat_container = st.container(height=500, border=False)

    with chat_container:
        st.markdown("""
        <div style="text-align:center;padding:30px 0 20px">
            <div style="font-size:2.5em">🤖</div>
            <div style="font-size:1.1em;color:#667eea;font-weight:600">AI 智能客服系统</div>
            <div style="font-size:0.85em;color:#94a3b8;margin-top:4px">
                基于知识库的智能问答 · 支持上下文对话 · 实时响应
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.markdown("""
            <div style="background:#f8f9fc;border-radius:12px;padding:20px;margin:16px 0;
                        border:1px dashed #cbd5e1">
                <div style="font-size:0.9em;color:#64748b;text-align:center">
                    👋 你好！我是 AI 智能客服，有什么可以帮你的吗？
                </div>
                <div style="margin-top:12px;display:flex;flex-wrap:wrap;gap:8px;justify-content:center">
                    <span style="background:white;padding:6px 14px;border-radius:20px;font-size:0.8em;
                                 border:1px solid #e2e8f0;color:#667eea">🖥️ 产品使用帮助</span>
                    <span style="background:white;padding:6px 14px;border-radius:20px;font-size:0.8em;
                                 border:1px solid #e2e8f0;color:#667eea">💰 价格与套餐</span>
                    <span style="background:white;padding:6px 14px;border-radius:20px;font-size:0.8em;
                                 border:1px solid #e2e8f0;color:#667eea">🔧 技术支持</span>
                    <span style="background:white;padding:6px 14px;border-radius:20px;font-size:0.8em;
                                 border:1px solid #e2e8f0;color:#667eea">📦 订单与物流</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                render_chat_message(
                    msg["role"], msg["content"],
                    msg.get("sources"), msg.get("timestamp")
                )

    # 满意度评分
    if st.session_state.show_rating and st.session_state.current_conv_id:
        if not has_rating(st.session_state.current_conv_id):
            with st.container():
                st.markdown("---")
                cols = st.columns([1, 5, 1])
                with cols[1]:
                    st.markdown("#### ⭐ 请为本次服务评分")
                    score = st.radio(
                        "满意度", [1, 2, 3, 4, 5],
                        format_func=lambda x: "☹️" * (6 - x) + "😊" * x,
                        horizontal=True, index=4
                    )
                    comment = st.text_input("补充说明（可选）", placeholder="说说你的感受...")
                    if st.button("提交评分", use_container_width=True):
                        add_rating(st.session_state.current_conv_id, score, comment or None)
                        st.session_state.show_rating = False
                        st.success("感谢你的反馈！🌟")
                        st.rerun()

    # 输入区域
    st.markdown("---")
    input_cols = st.columns([1, 6, 1, 1])
    with input_cols[1]:
        user_input = st.text_area(
            "输入你的问题",
            placeholder="请输入你想咨询的问题...",
            height=80,
            key="chat_input",
            label_visibility="collapsed"
        )
    with input_cols[2]:
        send_clicked = st.button("📤 发送", use_container_width=True, type="primary")

    if send_clicked and user_input.strip():
        # 如果没有活跃对话，创建新对话
        if not st.session_state.current_conv_id:
            st.session_state.current_conv_id = create_conversation(user["id"])

        # 保存用户消息
        add_message(st.session_state.current_conv_id, "user", user_input.strip())
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip(),
            "timestamp": datetime.now().strftime("%H:%M")
        })

        # AI 生成回复
        ai_engine = get_ai_engine()
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.chat_history
        ]

        with st.spinner("🤖 正在思考中..."):
            result = ai_engine.chat(user_input.strip(), history)

        # 保存 AI 回复
        sources_str = None
        if result["sources"]:
            sources_str = str(result["sources"])
        add_message(
            st.session_state.current_conv_id, "assistant",
            result["answer"], sources_str
        )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "from_knowledge": result["from_knowledge"],
            "timestamp": datetime.now().strftime("%H:%M")
        })

        st.session_state.show_rating = True
        st.rerun()


if __name__ == "__main__":
    main()
