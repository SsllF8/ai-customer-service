"""
AI 智能客服系统 - AI 引擎模块
基于 RAG（检索增强生成）的智能问答引擎
集成 DeepSeek API + ChromaDB 向量数据库
"""
import os
import json
import re
from typing import Optional

from openai import OpenAI
import chromadb
from chromadb.utils import embedding_functions

# 使用本地缓存的模型，避免每次启动都请求 HuggingFace Hub
os.environ.setdefault("HF_HUB_OFFLINE", "1")

# DeepSeek API 配置
DEEPSEEK_API_KEY = ""
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# ChromaDB 配置
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "customer_service_kb"

# 客服系统提示词
SYSTEM_PROMPT = """你是一个专业、友好、耐心的智能客服助手。你的职责是：
1. 基于知识库内容准确回答用户问题
2. 如果知识库中没有相关信息，诚实说明并给出通用建议
3. 保持专业但温暖的语气
4. 回答要简洁明了，重点突出
5. 如果用户问题涉及投诉或复杂问题，建议转接人工客服

回答格式：
- 直接给出答案，不要重复问题
- 如果有多个要点，用编号列表
- 在回答末尾可以适当引导用户继续提问"""

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class CustomerServiceAI:
    """AI 智能客服引擎"""

    def __init__(self):
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        # 使用 EphemeralClient（内存模式），避免 PersistentClient 在 Streamlit rerun 时
        # 重复创建导致的 Rust bindings 冲突
        self.chroma_client = chromadb.EphemeralClient()
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
        # 启动时从持久化目录加载数据（如果有的话）
        self._load_from_disk()

    def add_knowledge(self, text: str, source: str = "manual"):
        """添加知识到向量数据库"""
        chunks = self._split_text(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{source}_{len(self.collection.get()['ids']) + i}"
            self.collection.add(
                documents=[chunk],
                metadatas=[{"source": source, "chunk_index": i}],
                ids=[chunk_id]
            )
        return len(chunks)

    def add_knowledge_batch(self, chunks: list, source: str):
        """批量添加知识块"""
        if not chunks:
            return 0
        existing = self.collection.get()["ids"]
        base_index = len(existing)
        ids = [f"{source}_{base_index + i}" for i in range(len(chunks))]
        metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )
        return len(chunks)

    def search_knowledge(self, query: str, top_k: int = 3) -> list:
        """从知识库中检索相关内容"""
        if self.collection.count() == 0:
            return []
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count())
        )
        sources = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                sources.append({
                    "content": doc,
                    "source": metadata.get("source", "未知"),
                    "relevance": round(1 - distance, 3) if distance <= 1 else round(distance, 3)
                })
        return sources

    def chat(self, user_message: str, chat_history: list = None) -> dict:
        """
        处理用户消息并生成回复
        
        Args:
            user_message: 用户输入的消息
            chat_history: 对话历史 [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            {"answer": str, "sources": list, "from_knowledge": bool}
        """
        # 1. 检索知识库
        knowledge_results = self.search_knowledge(user_message, top_k=3)
        from_knowledge = len(knowledge_results) > 0

        # 2. 构建增强提示词
        knowledge_context = ""
        if knowledge_results:
            knowledge_parts = []
            for i, item in enumerate(knowledge_results, 1):
                if item["relevance"] > 0.3:
                    knowledge_parts.append(f"[参考资料{i}] {item['content']}")
            if knowledge_parts:
                knowledge_context = "\n\n以下是从知识库中检索到的相关信息，请优先基于这些信息回答：\n" + "\n".join(knowledge_parts)

        # 3. 构建消息列表
        messages = [{"role": "system", "content": SYSTEM_PROMPT + knowledge_context}]

        # 加入历史对话（最近5轮）
        if chat_history:
            recent_history = chat_history[-10:]
            for msg in recent_history:
                if msg.get("role") in ("user", "assistant"):
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"][:500]
                    })

        messages.append({"role": "user", "content": user_message})

        # 4. 调用 DeepSeek 生成回复
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"抱歉，AI 服务暂时不可用，请稍后再试。（错误：{str(e)[:100]}）"

        # 5. 格式化来源信息
        sources = []
        if knowledge_results:
            for item in knowledge_results:
                if item["relevance"] > 0.3:
                    sources.append(item)

        return {
            "answer": answer,
            "sources": sources,
            "from_knowledge": from_knowledge
        }

    def get_kb_stats(self) -> dict:
        """获取知识库统计"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": COLLECTION_NAME
        }

    def clear_knowledge(self, source: str = None):
        """清空知识库（可按来源清除）"""
        if source:
            results = self.collection.get(where={"source": source})
            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
        else:
            self.chroma_client.delete_collection(COLLECTION_NAME)
            self.collection = self.chroma_client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"}
            )

    def _split_text(self, text: str, max_length: int = 500, overlap: int = 50) -> list:
        """将长文本分割成块"""
        text = text.strip()
        if len(text) <= max_length:
            return [text] if text else []

        # 按段落分割
        paragraphs = re.split(r'\n\n+', text)
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk = current_chunk + "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # 段落本身太长则按句子切分
                if len(para) > max_length:
                    sentences = re.split(r'[。！？\n]', para)
                    temp = ""
                    for sent in sentences:
                        sent = sent.strip()
                        if not sent:
                            continue
                        if len(temp) + len(sent) + 1 <= max_length:
                            temp = temp + "。" + sent if temp else sent
                        else:
                            if temp:
                                chunks.append(temp.strip())
                            temp = sent
                    if temp:
                        chunks.append(temp.strip())
                else:
                    current_chunk = para
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _load_from_disk(self):
        """从磁盘加载知识库数据（JSON 备份）"""
        backup_file = os.path.join(CHROMA_DIR, "kb_backup.json")
        if os.path.exists(backup_file):
            try:
                with open(backup_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("documents"):
                    self.collection.add(
                        documents=data["documents"],
                        metadatas=data.get("metadatas", []),
                        ids=data.get("ids", [])
                    )
            except Exception:
                pass

    def save_to_disk(self):
        """保存知识库数据到磁盘"""
        os.makedirs(CHROMA_DIR, exist_ok=True)
        try:
            data = self.collection.get()
            if data and data["ids"]:
                backup_file = os.path.join(CHROMA_DIR, "kb_backup.json")
                with open(backup_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass


def load_faq_file(filepath: str) -> list:
    """
    从文件加载 FAQ 数据
    支持 TXT（问答对）和 JSON 格式
    
    TXT 格式示例：
        Q: 如何重置密码？
        A: 请访问设置页面，点击"修改密码"...
        
        Q: 你们的退款政策是什么？
        A: 支持7天无理由退款...
    
    JSON 格式示例：
        [
            {"q": "如何重置密码？", "a": "请访问设置页面..."},
            {"q": "退款政策", "a": "支持7天无理由退款..."}
        ]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if filepath.endswith(".json"):
        try:
            data = json.loads(content)
            chunks = []
            for item in data:
                if isinstance(item, dict):
                    q = item.get("q", item.get("question", item.get("问题", "")))
                    a = item.get("a", item.get("answer", item.get("回答", "")))
                    if q and a:
                        chunks.append(f"问题：{q}\n回答：{a}")
                elif isinstance(item, str):
                    chunks.append(item)
            return chunks
        except json.JSONDecodeError:
            pass

    # TXT 格式解析
    chunks = []
    lines = content.split("\n")
    current_q = ""
    current_a = ""

    for line in lines:
        line = line.strip()
        if not line:
            if current_q and current_a:
                chunks.append(f"问题：{current_q}\n回答：{current_a}")
                current_q = ""
                current_a = ""
            continue

        # 匹配问题行
        q_match = re.match(r'^(?:Q：|Q:|问题：|问题:)\s*(.+)', line)
        a_match = re.match(r'^(?:A：|A:|回答：|回答:)\s*(.+)', line)

        if q_match:
            if current_q and current_a:
                chunks.append(f"问题：{current_q}\n回答：{current_a}")
            current_q = q_match.group(1).strip()
            current_a = ""
        elif a_match:
            current_a += a_match.group(1).strip()
        elif current_q:
            # 续行内容
            if current_a:
                current_a += " " + line
            else:
                current_a = line

    if current_q and current_a:
        chunks.append(f"问题：{current_q}\n回答：{current_a}")

    return chunks


# 全局实例
_ai_instance = None


def get_ai_engine() -> CustomerServiceAI:
    """获取 AI 引擎单例"""
    global _ai_instance
    if _ai_instance is None:
        # 加载 .env 并设置 API Key
        from dotenv import load_dotenv
        load_dotenv()
        global DEEPSEEK_API_KEY
        DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        _ai_instance = CustomerServiceAI()
    return _ai_instance
