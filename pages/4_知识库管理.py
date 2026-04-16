"""
AI 智能客服系统 - 管理后台 - 知识库管理
"""
import os
import streamlit as st
import tempfile
from database import init_db, get_knowledge_docs, add_knowledge_doc, delete_knowledge_doc
init_db()
from ai_engine import get_ai_engine, load_faq_file


KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")


def get_engine():
    """延迟加载 AI 引擎，带提示"""
    with st.spinner("🔄 正在加载 AI 引擎（首次需下载 Embedding 模型，约 90MB）..."):
        return get_ai_engine()


def main():
    st.title("📚 知识库管理")

    # 已上传文档列表（不需要 AI 引擎）
    docs = get_knowledge_docs()

    # 知识库概览 - 文档数不需要 AI 引擎
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;
                padding:24px;color:white;margin-bottom:20px">
        <div style="font-size:1.1em;font-weight:600">🧠 知识库概览</div>
        <div style="display:flex;gap:40px;margin-top:12px">
            <div>
                <div style="font-size:2em;font-weight:700">{len(docs)}</div>
                <div style="font-size:0.85em;opacity:0.9">已上传文档</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 加载 AI 引擎（用户点击后）
    if st.button("🔄 加载 AI 引擎", use_container_width=True):
        try:
            ai_engine = get_engine()
            kb_stats = ai_engine.get_kb_stats()
            st.session_state["ai_engine_loaded"] = True
            st.session_state["kb_chunks"] = kb_stats["total_chunks"]
            st.success(f"✅ 引擎加载完成，向量索引：{kb_stats['total_chunks']} 条")
        except Exception as e:
            st.error(f"❌ 引擎加载失败：{str(e)}")

    if "ai_engine_loaded" not in st.session_state:
        st.info("💡 点击上方按钮加载 AI 引擎后，即可使用知识库管理功能。首次加载需要下载 Embedding 模型（约 90MB），请耐心等待。")
        return

    ai_engine = get_ai_engine()

    # 上传文档
    st.subheader("📤 上传知识文档")

    upload_col1, upload_col2 = st.columns([1, 1])

    with upload_col1:
        st.markdown("**方式一：上传文件**")
        st.caption("支持 .txt（FAQ 格式）和 .json 格式")
        uploaded_file = st.file_uploader(
            "选择文件",
            type=["txt", "json"],
            key="knowledge_upload"
        )
        if uploaded_file:
            if st.button("📄 导入文件到知识库", use_container_width=True, type="primary"):
                try:
                    # 保存到临时文件
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, mode="w", encoding="utf-8") as f:
                        f.write(uploaded_file.read().decode("utf-8"))
                        tmp_path = f.name

                    chunks = load_faq_file(tmp_path)
                    os.unlink(tmp_path)

                    if chunks:
                        chunk_count = ai_engine.add_knowledge_batch(chunks, uploaded_file.name)
                        add_knowledge_doc(uploaded_file.name, "faq", chunk_count)
                        ai_engine.save_to_disk()
                        st.success(f"✅ 成功导入 {chunk_count} 条知识！来源：{uploaded_file.name}")
                        st.rerun()
                    else:
                        st.error("❌ 文件内容为空或格式无法识别。")
                except Exception as e:
                    st.error(f"❌ 导入失败：{str(e)}")

    with upload_col2:
        st.markdown("**方式二：手动添加**")
        st.caption("直接输入问答对，适合少量补充")
        manual_q = st.text_area("问题", placeholder="例如：如何重置密码？", height=60, key="manual_q")
        manual_a = st.text_area("回答", placeholder="例如：请访问设置页面，点击'修改密码'...", height=120, key="manual_a")
        if st.button("✏️ 添加到知识库", use_container_width=True):
            if manual_q.strip() and manual_a.strip():
                chunk_count = ai_engine.add_knowledge(
                    f"问题：{manual_q.strip()}\n回答：{manual_a.strip()}",
                    "manual_entry"
                )
                ai_engine.save_to_disk()
                st.success(f"✅ 添加成功！知识库条目：{kb_stats['total_chunks'] + chunk_count}")
                st.rerun()
            else:
                st.warning("请填写问题和回答。")

    # 知识检索测试
    st.markdown("---")
    st.subheader("🔍 知识检索测试")
    test_query = st.text_input("输入测试问题", placeholder="输入一个问题，测试知识库检索效果...")
    if test_query.strip():
        results = ai_engine.search_knowledge(test_query, top_k=3)
        if results:
            for i, r in enumerate(results, 1):
                st.markdown(f"""
                <div style="background:#f8f9fc;padding:12px 16px;border-radius:10px;
                            margin:6px 0;border-left:3px solid #667eea">
                    <div style="display:flex;justify-content:space-between">
                        <span style="color:#667eea;font-weight:600;font-size:0.85em">结果 #{i}</span>
                        <span style="color:#94a3b8;font-size:0.8em">相关度：{r['relevance']}</span>
                    </div>
                    <div style="margin-top:4px;color:#475569;line-height:1.5">
                        {r['content'][:200]}{'...' if len(r['content']) > 200 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("未检索到相关内容。知识库可能为空或问题与知识库内容不匹配。")

    # 已上传文档列表
    st.markdown("---")
    st.subheader("📂 已上传文档")
    docs = get_knowledge_docs()
    if docs:
        for doc in docs:
            doc_col1, doc_col2, doc_col3 = st.columns([3, 1, 1])
            with doc_col1:
                st.markdown(f"**📄 {doc['filename']}**")
                st.caption(f"类型：{doc['doc_type']} · 条目：{doc['chunk_count']} · 上传时间：{doc['uploaded_at'][:16]}")
            with doc_col3:
                if st.button("🗑️ 删除", key=f"del_{doc['id']}", use_container_width=True):
                    delete_knowledge_doc(doc["id"])
                    try:
                        ai_engine.clear_knowledge(doc["filename"])
                        ai_engine.save_to_disk()
                    except Exception:
                        pass
                    st.success("已删除")
                    st.rerun()
    else:
        st.info("暂无已上传的文档。")

    # 危险操作
    st.markdown("---")
    st.subheader("⚠️ 危险操作")
    if st.button("🗑️ 清空全部知识库", type="secondary"):
        st.warning("确定要清空知识库吗？此操作不可撤销！")
        if st.button("确认清空", type="primary"):
            ai_engine.clear_knowledge()
            ai_engine.save_to_disk()
            st.success("知识库已清空。")
            st.rerun()


if __name__ == "__main__":
    main()
