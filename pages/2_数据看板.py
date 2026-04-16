"""
AI 智能客服系统 - 管理后台 - 数据看板
"""
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from database import init_db, get_dashboard_stats, get_hot_questions, get_rating_distribution, get_daily_stats
init_db()


def main():
    st.title("📊 数据看板")

    stats = get_dashboard_stats()

    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);border-radius:12px;
                    padding:20px;color:white;text-align:center">
            <div style="font-size:2em;font-weight:700">{stats['today_convs']}</div>
            <div style="font-size:0.85em;opacity:0.9;margin-top:4px">今日对话</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f093fb,#f5576c);border-radius:12px;
                    padding:20px;color:white;text-align:center">
            <div style="font-size:2em;font-weight:700">{stats['today_questions']}</div>
            <div style="font-size:0.85em;opacity:0.9;margin-top:4px">今日提问</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#4facfe,#00f2fe);border-radius:12px;
                    padding:20px;color:white;text-align:center">
            <div style="font-size:2em;font-weight:700">{stats['avg_rating']}</div>
            <div style="font-size:0.85em;opacity:0.9;margin-top:4px">平均满意度 ⭐</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#43e97b,#38f9d7);border-radius:12px;
                    padding:20px;color:white;text-align:center">
            <div style="font-size:2em;font-weight:700">{stats['handover_count']}</div>
            <div style="font-size:0.85em;opacity:0.9;margin-top:4px">人工接管</div>
        </div>
        """, unsafe_allow_html=True)

    # 汇总统计
    st.markdown("---")
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    with sum_col1:
        st.metric("📈 累计对话数", stats["total_convs"])
    with sum_col2:
        st.metric("💬 累计提问数", stats["total_questions"])
    with sum_col3:
        st.metric("📚 知识库文档", f"{stats['doc_count']} 篇")

    # 图表区域
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("📊 满意度分布")
        rating_dist = get_rating_distribution()
        if rating_dist:
            fig, ax = plt.subplots(figsize=(6, 3))
            scores = sorted(rating_dist.keys())
            counts = [rating_dist[s] for s in scores]
            colors = ['#ff6b6b', '#ffa07a', '#ffd700', '#90ee90', '#667eea']
            bars = ax.bar(scores, counts, color=colors[:len(scores)], edgecolor='white', linewidth=1.5)
            ax.set_xlabel("评分", fontsize=10)
            ax.set_ylabel("次数", fontsize=10)
            ax.set_title("用户满意度评分分布", fontsize=11, fontweight='bold')
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                       str(count), ha='center', va='bottom', fontweight='bold')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("暂无评分数据")

    with chart_col2:
        st.subheader("📈 每日趋势")
        daily = get_daily_stats(7)
        if daily:
            fig, ax = plt.subplots(figsize=(6, 3))
            dates = [d["date"][-5:] for d in daily]
            convs = [d["conversations"] for d in daily]
            questions = [d["questions"] for d in daily]

            ax.plot(dates, convs, 'o-', color='#667eea', linewidth=2, markersize=6, label='对话数')
            ax.plot(dates, questions, 's--', color='#f5576c', linewidth=2, markersize=6, label='提问数')
            ax.fill_between(dates, convs, alpha=0.1, color='#667eea')
            ax.set_xlabel("日期", fontsize=10)
            ax.set_ylabel("数量", fontsize=10)
            ax.set_title("近7天对话趋势", fontsize=11, fontweight='bold')
            ax.legend(fontsize=9)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("暂无趋势数据")

    # 热门问题
    st.markdown("---")
    st.subheader("🔥 热门问题 TOP 10")
    hot = get_hot_questions(10)
    if hot:
        for i, q in enumerate(hot, 1):
            col_left, col_mid, col_right = st.columns([1, 6, 1])
            with col_left:
                badge_color = ["#f5576c", "#ff6b6b", "#ffa07a"][min(i-1, 2)] if i <= 3 else "#94a3b8"
                st.markdown(
                    f'<span style="background:{badge_color};color:white;padding:4px 10px;'
                    f'border-radius:12px;font-size:0.85em;font-weight:600">#{i}</span>',
                    unsafe_allow_html=True
                )
            with col_right:
                st.markdown(f"**{q['content'][:80]}{'...' if len(q['content']) > 80 else ''}**")
            with st.columns([1, 6, 1])[2]:
                st.markdown(f"<span style='color:#94a3b8;font-size:0.85em'>×{q['count']}</span>", unsafe_allow_html=True)
    else:
        st.info("暂无问题数据，等用户开始聊天后这里会显示热门问题。")


if __name__ == "__main__":
    main()
