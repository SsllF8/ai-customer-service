# 🤖 AI 智能客服系统 | AI Customer Service System

> [中文](#中文) | [English](#english)

---

<a id="中文"></a>
## 🇨🇳 中文

> 基于 RAG（检索增强生成）的企业级智能客服系统，集成 DeepSeek API + ChromaDB + SQLite，提供完整的客服问答、数据统计和管理后台功能。5 页面多页面架构，是最复杂的一个项目。

![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-red?logo=streamlit)
![DeepSeek](https://img.shields.io/badge/DeepSeek-API-blue)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.0.9+-orange)
![SQLite](https://img.shields.io/badge/SQLite-3+-blue)
![matplotlib](https://img.shields.io/badge/matplotlib-3.8+-green)

### 📸 截图预览

| 首页 | 智能客服 |
|:---:|:---:|
| ![首页](screenshots/01_home.png) | ![智能客服](screenshots/02_chat.png) |

| 数据看板 | 对话记录 |
|:---:|:---:|
| ![数据看板](screenshots/03_dashboard.png) | ![对话记录](screenshots/04_conversations.png) |

| 知识库管理 |
|:---:|
| ![知识库管理](screenshots/05_knowledge_base.png) |

### ✨ 功能特性

#### 💬 智能客服页面
- 基于 RAG 的知识库问答 — AI 从 FAQ 文档中检索相关内容，生成精准回答
- 对话上下文记忆 — 自动保留最近 5 轮对话历史，理解上下文
- 满意度评分 — 用户可对回答打分（1-5 星），支持评论反馈
- 人工接管标记 — 复杂问题一键转接人工客服

#### 📊 数据看板页面
- 实时统计卡片 — 今日对话数、总提问数、平均满意度、知识库文档数
- 满意度分布图（matplotlib 饼图）
- 每日趋势图（近 7 天对话量折线图）
- 热门问题 TOP 10 排行

#### 💬 对话记录页面
- 全量对话详情查看（用户消息 + AI 回复 + 知识来源）
- 按状态筛选（活跃/已结束/人工接管）
- 评分标签展示

#### 📚 知识库管理页面
- 上传 FAQ 文档（支持 .txt 和 .json 格式）
- 手动添加问答对
- 知识检索测试 — 输入问题验证检索效果
- 知识库条目管理（查看/删除）
- 一键清空知识库

### 🏗️ 系统架构

```
用户输入 → AI 引擎 → DeepSeek API
                ↓
         ChromaDB 向量检索（知识库）
                ↓
         上下文记忆 + 知识增强提示词
                ↓
         生成回答 → 返回用户
                ↓
         SQLite 存储对话记录、评分、统计
```

### 📁 项目结构

```
ai-customer-service/
├── app.py                  # 主入口（首页）
├── ai_engine.py            # AI 引擎模块（RAG + DeepSeek）
├── database.py             # 数据库模块（SQLite）
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量配置
├── knowledge_base/
│   └── default_faq.txt     # 示例 FAQ 文档
├── screenshots/            # 项目截图
├── data/                   # SQLite 数据库文件（自动生成）
├── pages/
│   ├── 1_智能客服.py        # 用户聊天页面
│   ├── 2_数据看板.py        # 数据统计看板
│   ├── 3_对话记录.py        # 对话记录管理
│   └── 4_知识库管理.py      # 知识库管理后台
```

### 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| [DeepSeek API](https://platform.deepseek.com/) | AI 对话生成 |
| [ChromaDB](https://www.trychroma.com/) | 向量数据库（知识库检索） |
| [Streamlit](https://streamlit.io/) | Web 界面框架（多页面架构） |
| [SQLite](https://www.sqlite.org/) | 对话记录与统计数据持久化 |
| [matplotlib](https://matplotlib.org/) | 数据可视化图表 |
| [Sentence-Transformers](https://www.sbert.net/) | 文本向量化（all-MiniLM-L6-v2） |

### 🚀 快速开始

```bash
git clone https://github.com/SsllF8/ai-customer-service.git
cd ai-customer-service
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env  # 填入 DEEPSEEK_API_KEY
streamlit run app.py --server.port 8501
```

浏览器访问 `http://localhost:8501` 即可使用。

### 📖 使用指南

**首次使用：**
1. 进入「📚 知识库管理」页面
2. 点击「🔄 加载 AI 引擎」（首次需下载 Embedding 模型，约 90MB）
3. 上传 FAQ 文档或手动添加问答对
4. 回到「💬 智能客服」开始对话

**FAQ 文档格式：**

TXT 格式：
```
Q: 如何注册账号？
A: 点击首页右上角的"注册"按钮，填写手机号和验证码即可完成注册。

Q: 退款政策是什么？
A: 购买 7 天内支持无理由退款，请在"我的订单"中提交退款申请。
```

JSON 格式：
```json
[
  {"q": "如何注册账号？", "a": "点击首页右上角的注册按钮..."},
  {"q": "退款政策是什么？", "a": "购买7天内支持无理由退款..."}
]
```

### 💡 应用场景

**企业客服：**
- **电商客服** — 上传商品 FAQ、退换货政策，AI 自动回答常见问题
- **SaaS 产品** — 导入产品文档、使用教程，降低人工客服成本
- **教育机构** — 录入招生政策、课程信息，24 小时自动答疑

**个人项目：**
- **作品集展示** — 展示全栈 AI 应用开发能力
- **技术学习** — 深入理解 RAG 原理、向量检索、数据库设计
- **面试加分** — 多页面架构、数据持久化、数据可视化等技术亮点

### 🎯 与其他项目的区别

| 特性 | 前五个项目 | 本项目 |
|------|-----------|--------|
| 数据存储 | 无/文件 | **SQLite 数据库** |
| 页面架构 | 单页面 | **多页面（5 页）** |
| 数据可视化 | 无 | **matplotlib 图表** |
| 后台管理 | 无 | **完整的 CRUD 管理** |
| 复杂度 | 低-中 | **高** |

### 💡 面试要点 / Interview Talking Points

**1. 为什么这个项目用多页面架构？**
- 客服系统天然有多个功能模块：聊天、看板、记录、管理
- 单页面会导致代码臃肿、UI 拥挤
- Streamlit 多页面通过 `pages/` 目录实现，每个 page 独立文件

**2. 多页面架构有什么坑？**
- 每个 page 是独立进程，`app.py` 的代码不保证先执行
- **必须在每个 page 里单独调用 `init_db()` 和 `load_dotenv()`**
- 全局状态用 `st.session_state` 共享，不能用全局变量

**3. 为什么选 SQLite？**
- 零配置、无需安装数据库服务
- 适合中小规模的对话记录存储
- Streamlit 部署时最方便的持久化方案

**4. ChromaDB 在这里和 RAG 知识库项目有什么不同？**
- RAG 知识库项目用 PersistentClient（持久化到磁盘）
- 本项目用 **EphemeralClient（内存模式）+ JSON 文件备份**
- 原因：Streamlit rerun 时 PersistentClient 会反复创建，导致 Rust bindings 报错（`'RustBindingsAPI' object has no attribute 'bindings'`）

**5. 数据看板的图表怎么做？**
- 用 matplotlib 直接生成图表，嵌入 Streamlit 的 `st.pyplot()`
- 饼图展示满意度分布，折线图展示每日趋势
- 数据从 SQLite 查询聚合（GROUP BY, COUNT, AVG）

**6. 上下文记忆怎么实现的？**
- 用 `st.session_state` 保存最近 5 轮对话
- 每次提问时，把历史对话拼接到 prompt 中
- 限制轮数避免 token 溢出

### ⚠️ 搭建中可能遇到的问题 / Troubleshooting

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| ChromaDB Rust bindings 报错 | Streamlit rerun 时 PersistentClient 重复创建 | 换用 EphemeralClient + JSON 备份 |
| Embedding 模型下载慢 | 首次运行需下载 ~90MB | 耐心等待，或设置 `HF_HUB_OFFLINE=1` 用缓存 |
| 页面间状态丢失 | 每个页面独立加载 | 用 `st.session_state` 共享状态 |
| .env 加载失败 | 某个 page 没调用 `load_dotenv()` | 在每个 page 文件顶部加入 `load_dotenv()` |
| 看板数据为空 | 数据库未初始化 | 确保每个页面都调用了 `init_db()` |
| matplotlib 中文显示方块 | 缺少中文字体 | `plt.rcParams['font.sans-serif'] = ['SimHei']` |
| chromadb 版本冲突 | 1.0.9 之后的 API 变化 | 锁定版本：`chromadb==1.0.9` |

### 🚀 扩展方向 / Future Enhancements

- **用户认证** — 添加登录/注册功能，区分普通用户和管理员
- **实时推送** — WebSocket 实现实时消息推送（替代轮询）
- **多轮对话优化** — 基于 session 的完整对话管理，支持历史回溯
- **AI 训练反馈闭环** — 用户低评分的回答自动标记，用于优化知识库
- **智能路由** — AI 判断问题类型，自动路由到不同部门/知识库
- **多语言支持** — 知识库按语言分组，自动检测用户语言
- **API 接口** — 提供 REST API，支持接入微信/钉钉/飞书
- **前端重构** — 用 React/Vue 重写前端，实现 WebSocket 实时通信
- **监控告警** — 对话量异常、满意度下降时自动告警
- **A/B 测试** — 支持多套 prompt 模板，对比回答效果

---

<a id="english"></a>
## 🇬🇧 English

> An enterprise-grade AI customer service system based on RAG (Retrieval-Augmented Generation), integrating DeepSeek API + ChromaDB + SQLite. Provides complete customer service Q&A, analytics dashboard, and admin management. 5-page multi-page architecture — the most complex project in the portfolio.

### Screenshots

| Home | Customer Service Chat |
|:---:|:---:|
| ![Home](screenshots/01_home.png) | ![Chat](screenshots/02_chat.png) |

| Analytics Dashboard | Conversation History |
|:---:|:---:|
| ![Dashboard](screenshots/03_dashboard.png) | ![History](screenshots/04_conversations.png) |

| Knowledge Base Management |
|:---:|
| ![KB Management](screenshots/05_knowledge_base.png) |

### Features

#### 💬 Customer Service
- RAG-based knowledge base Q&A with source citations
- Conversation context memory (last 5 turns)
- Satisfaction rating (1-5 stars) with comment feedback
- Human agent handoff for complex queries

#### 📊 Analytics Dashboard
- Real-time stat cards: today's conversations, total questions, avg satisfaction, KB document count
- Satisfaction distribution pie chart (matplotlib)
- Daily trend line chart (7-day conversation volume)
- Top 10 hot questions ranking

#### 💬 Conversation History
- Full conversation detail view (user message + AI reply + knowledge source)
- Filter by status (active/ended/human-handoff)
- Rating tag display

#### 📚 Knowledge Base Management
- Upload FAQ documents (.txt and .json formats)
- Manual Q&A pair creation
- Knowledge retrieval testing — verify search quality
- Entry management (view/delete)
- One-click knowledge base clear

### Architecture

```
User Input → AI Engine → DeepSeek API
                ↓
         ChromaDB Vector Search (Knowledge Base)
                ↓
         Context Memory + Knowledge-Augmented Prompt
                ↓
         Generate Response → Return to User
                ↓
         SQLite Stores Conversation Logs, Ratings, Analytics
```

### Tech Stack

| Technology | Purpose |
|-----------|---------|
| DeepSeek API | AI conversation generation |
| ChromaDB | Vector database for knowledge retrieval |
| Streamlit | Multi-page web UI framework |
| SQLite | Conversation logs and analytics persistence |
| matplotlib | Data visualization charts |
| Sentence-Transformers | Text vectorization (all-MiniLM-L6-v2) |

### Quick Start

```bash
git clone https://github.com/SsllF8/ai-customer-service.git
cd ai-customer-service
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env  # Fill in your DEEPSEEK_API_KEY
streamlit run app.py --server.port 8501
```

### FAQ Document Format

**TXT:**
```
Q: How do I register?
A: Click the "Register" button in the top-right corner...

Q: What is the refund policy?
A: 7-day no-questions-asked refund...
```

**JSON:**
```json
[
  {"q": "How do I register?", "a": "Click the Register button..."},
  {"q": "What is the refund policy?", "a": "7-day refund..."}
]
```

### Interview Talking Points

**1. Why multi-page architecture?**
- Customer service has natural functional modules: chat, dashboard, history, admin
- Single page would be bloated and cluttered
- Streamlit multi-page via `pages/` directory, each page is an independent file

**2. Multi-page pitfalls?**
- Each page loads independently, `app.py` code doesn't execute first
- **Must call `init_db()` and `load_dotenv()` in every page**
- Use `st.session_state` for shared state, not global variables

**3. Why SQLite?**
- Zero-config, no database service needed
- Suitable for small-to-medium conversation volume
- Easiest persistence option for Streamlit deployment

**4. ChromaDB vs the RAG KB project?**
- RAG KB project used PersistentClient (disk persistence)
- This project uses **EphemeralClient (in-memory) + JSON file backup**
- Reason: Streamlit rerun causes PersistentClient recreation, leading to Rust bindings error

**5. How are dashboard charts built?**
- matplotlib generates charts, embedded via `st.pyplot()`
- Pie chart for satisfaction distribution, line chart for daily trends
- Data aggregated from SQLite queries (GROUP BY, COUNT, AVG)

**6. How is context memory implemented?**
- `st.session_state` stores last 5 conversation turns
- History appended to prompt on each query
- Turn limit prevents token overflow

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| ChromaDB Rust bindings error | PersistentClient recreated on Streamlit rerun | Switch to EphemeralClient + JSON backup |
| Slow embedding download | First run downloads ~90MB model | Wait, or set `HF_HUB_OFFLINE=1` for cache |
| State lost between pages | Each page loads independently | Use `st.session_state` for shared state |
| .env not loaded | Page didn't call `load_dotenv()` | Add `load_dotenv()` at top of every page |
| Dashboard shows empty data | DB not initialized | Ensure `init_db()` called in every page |
| matplotlib Chinese squares | Missing Chinese fonts | `plt.rcParams['font.sans-serif'] = ['SimHei']` |
| chromadb version conflict | API changes after 1.0.9 | Pin version: `chromadb==1.0.9` |

### Future Enhancements

- **User Authentication** — Login/register, separate user and admin roles
- **Real-time Push** — WebSocket for live message delivery
- **Multi-turn Optimization** — Session-based conversation management with history
- **Feedback Loop** — Auto-flag low-rated answers for KB improvement
- **Smart Routing** — AI classifies question type, routes to specialized KBs
- **Multi-language** — KB grouped by language, auto-detect user language
- **REST API** — Expose endpoints for WeChat/DingTalk/Feishu integration
- **Frontend Rewrite** — React/Vue with WebSocket real-time communication
- **Monitoring & Alerts** — Auto-alert on conversation anomalies or satisfaction drops
- **A/B Testing** — Multiple prompt templates with effectiveness comparison

## 📄 License

This project is licensed under the MIT License.
