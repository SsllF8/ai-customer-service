"""
AI 智能客服系统 - 数据库管理模块
使用 SQLite 存储对话记录、用户信息、满意度评分
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "customer_service.db")
_db_initialized = False


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '匿名用户',
            session_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 对话会话表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            status TEXT DEFAULT 'active',
            is_handover INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 消息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            sources TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    # 满意度评分表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)

    # 知识库文档表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_docs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            doc_type TEXT DEFAULT 'faq',
            chunk_count INTEGER DEFAULT 0,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ==================== 用户操作 ====================

def get_or_create_user(session_id, name=None):
    """获取或创建用户"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE session_id = ?", (session_id,))
    user = cursor.fetchone()
    if user:
        if name and name != user["name"]:
            cursor.execute("UPDATE users SET name = ? WHERE id = ?", (name, user["id"]))
            conn.commit()
        conn.close()
        return dict(user)
    cursor.execute(
        "INSERT INTO users (name, session_id) VALUES (?, ?)",
        (name or "匿名用户", session_id)
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    conn.close()
    return user


# ==================== 对话操作 ====================

def create_conversation(user_id):
    """创建新对话"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO conversations (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    conv_id = cursor.lastrowid
    conn.close()
    return conv_id


def add_message(conversation_id, role, content, sources=None):
    """添加消息"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (conversation_id, role, content, sources) VALUES (?, ?, ?, ?)",
        (conversation_id, role, content, sources)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id


def get_conversation_messages(conversation_id):
    """获取对话的所有消息"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, sources, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at",
        (conversation_id,)
    )
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages


def get_active_conversation(user_id):
    """获取用户当前活跃对话"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM conversations WHERE user_id = ? AND status = 'active' ORDER BY started_at DESC LIMIT 1",
        (user_id,)
    )
    conv = cursor.fetchone()
    conn.close()
    return dict(conv) if conv else None


def end_conversation(conversation_id):
    """结束对话"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET status = 'ended', ended_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,)
    )
    conn.commit()
    conn.close()


def mark_handover(conversation_id):
    """标记为人工接管"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE conversations SET is_handover = 1 WHERE id = ?",
        (conversation_id,)
    )
    conn.commit()
    conn.close()


# ==================== 评分操作 ====================

def add_rating(conversation_id, score, comment=None):
    """添加满意度评分"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ratings (conversation_id, score, comment) VALUES (?, ?, ?)",
        (conversation_id, score, comment)
    )
    conn.commit()
    conn.close()


def has_rating(conversation_id):
    """检查对话是否已评分"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) as cnt FROM ratings WHERE conversation_id = ?",
        (conversation_id,)
    )
    count = cursor.fetchone()["cnt"]
    conn.close()
    return count > 0


# ==================== 统计查询 ====================

def get_dashboard_stats():
    """获取仪表盘统计数据"""
    conn = get_connection()
    cursor = conn.cursor()

    # 今日对话数
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM conversations
        WHERE DATE(started_at) = DATE('now', 'localtime')
    """)
    today_convs = cursor.fetchone()["cnt"]

    # 总对话数
    cursor.execute("SELECT COUNT(*) as cnt FROM conversations")
    total_convs = cursor.fetchone()["cnt"]

    # 总消息数
    cursor.execute("SELECT COUNT(*) as cnt FROM messages WHERE role = 'user'")
    total_questions = cursor.fetchone()["cnt"]

    # 平均满意度
    cursor.execute("SELECT AVG(score) as avg_score FROM ratings")
    avg_rating = cursor.fetchone()["avg_score"] or 0

    # 评分数量
    cursor.execute("SELECT COUNT(*) as cnt FROM ratings")
    rating_count = cursor.fetchone()["cnt"]

    # 人工接管次数
    cursor.execute("SELECT COUNT(*) as cnt FROM conversations WHERE is_handover = 1")
    handover_count = cursor.fetchone()["cnt"]

    # 知识库文档数
    cursor.execute("SELECT COUNT(*) as cnt FROM knowledge_docs")
    doc_count = cursor.fetchone()["cnt"]

    # 今日消息数
    cursor.execute("""
        SELECT COUNT(*) as cnt FROM messages
        WHERE DATE(created_at) = DATE('now', 'localtime') AND role = 'user'
    """)
    today_questions = cursor.fetchone()["cnt"]

    conn.close()
    return {
        "today_convs": today_convs,
        "total_convs": total_convs,
        "total_questions": total_questions,
        "avg_rating": round(avg_rating, 1),
        "rating_count": rating_count,
        "handover_count": handover_count,
        "doc_count": doc_count,
        "today_questions": today_questions,
    }


def get_hot_questions(limit=10):
    """获取热门问题（出现频率最高的用户问题）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT content, COUNT(*) as count
        FROM messages
        WHERE role = 'user'
        GROUP BY LOWER(TRIM(content))
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    questions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return questions


def get_recent_conversations(limit=50):
    """获取最近的对话列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.id, c.started_at, c.ended_at, c.status, c.is_handover,
               u.name as user_name,
               (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id AND m.role = 'user') as msg_count,
               (SELECT AVG(r.score) FROM ratings r WHERE r.conversation_id = c.id) as rating
        FROM conversations c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.started_at DESC
        LIMIT ?
    """, (limit,))
    conversations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return conversations


def get_rating_distribution():
    """获取评分分布"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score, COUNT(*) as count
        FROM ratings
        GROUP BY score
        ORDER BY score
    """)
    distribution = {str(row["score"]): row["count"] for row in cursor.fetchall()}
    conn.close()
    return distribution


def get_daily_stats(days=7):
    """获取每日统计（最近N天）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DATE(started_at) as date,
               COUNT(*) as conversations,
               SUM(msg_count) as questions
        FROM conversations c
        LEFT JOIN (
            SELECT conversation_id, COUNT(*) as msg_count
            FROM messages WHERE role = 'user'
            GROUP BY conversation_id
        ) m ON c.id = m.conversation_id
        WHERE DATE(started_at) >= DATE('now', 'localtime', ?)
        GROUP BY DATE(started_at)
        ORDER BY date
    """, (f"-{days} days",))
    stats = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return stats


# ==================== 知识库文档操作 ====================

def add_knowledge_doc(filename, doc_type="faq", chunk_count=0):
    """添加知识库文档记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO knowledge_docs (filename, doc_type, chunk_count) VALUES (?, ?, ?)",
        (filename, doc_type, chunk_count)
    )
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id


def get_knowledge_docs():
    """获取所有知识库文档"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM knowledge_docs ORDER BY uploaded_at DESC")
    docs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return docs


def delete_knowledge_doc(doc_id):
    """删除知识库文档记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM knowledge_docs WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
