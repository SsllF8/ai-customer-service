"""
AI 智能客服系统 - 管理后台 - 对话记录
"""
import streamlit as st
from database import init_db, get_recent_conversations, get_conversation_messages
init_db()


def main():
    st.title("💬 对话记录")

    # 筛选条件
    filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
    with filter_col1:
        status_filter = st.selectbox(
            "对话状态",
            ["全部", "活跃", "已结束"],
            format_func=lambda x: {"全部": "📋 全部", "活跃": "🟢 活跃", "已结束": "⚫ 已结束"}[x]
        )
    with filter_col2:
        sort_order = st.selectbox("排序方式", ["最新优先", "最早优先"])

    # 获取对话列表
    conversations = get_recent_conversations(50)

    # 应用筛选
    if status_filter != "全部":
        conversations = [c for c in conversations if c["status"] == status_filter]
    if sort_order == "最早优先":
        conversations = conversations[::-1]

    if not conversations:
        st.info("暂无对话记录。")
        return

    # 选择对话查看详情
    st.subheader(f"📋 共 {len(conversations)} 条对话记录")

    selected_conv = st.selectbox(
        "选择对话查看详情",
        options=range(len(conversations)),
        format_func=lambda i: (
            f"[{conversations[i]['id']}] "
            f"{conversations[i]['user_name']} · "
            f"{conversations[i]['started_at'][:16]} · "
            f"{'🟢 活跃' if conversations[i]['status'] == 'active' else '⚫ 已结束'} · "
            f"{'⚠️ 人工接管' if conversations[i]['is_handover'] else '🤖 AI'} · "
            f"{conversations[i]['msg_count']}条消息"
        )
    )

    if selected_conv is not None:
        conv = conversations[selected_conv]

        # 对话详情卡片
        st.markdown("---")
        detail_cols = st.columns(4)
        with detail_cols[0]:
            st.metric("对话 ID", conv["id"])
        with detail_cols[1]:
            st.metric("用户", conv["user_name"])
        with detail_cols[2]:
            st.metric("消息数", conv["msg_count"])
        with detail_cols[3]:
            rating = f"⭐ {conv['rating']:.1f}" if conv["rating"] else "未评分"
            st.metric("满意度", rating)

        if conv["is_handover"]:
            st.warning("⚠️ 此对话已转接人工客服")

        # 消息列表
        messages = get_conversation_messages(conv["id"])
        if messages:
            st.markdown("---")
            st.subheader("📝 对话详情")
            for msg in messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background:#eef2ff;padding:12px 16px;border-radius:12px;
                                margin:8px 0;border-left:4px solid #667eea">
                        <span style="color:#667eea;font-weight:600;font-size:0.85em">👤 用户</span>
                        <span style="color:#94a3b8;font-size:0.8em;float:right">{msg['created_at'][:16]}</span>
                        <div style="margin-top:4px">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#f0fdf4;padding:12px 16px;border-radius:12px;
                                margin:8px 0;border-left:4px solid #43e97b">
                        <span style="color:#22c55e;font-weight:600;font-size:0.85em">🤖 AI 客服</span>
                        <span style="color:#94a3b8;font-size:0.8em;float:right">{msg['created_at'][:16]}</span>
                        <div style="margin-top:4px;white-space:pre-wrap">{msg['content']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("该对话暂无消息记录。")


if __name__ == "__main__":
    main()
