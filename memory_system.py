"""
流萤手机版 - 记忆系统
SQLite本地存储，支持短期/工作/长期记忆
"""
import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path


class MemorySystem:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "memories.db"
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 记忆表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'general',
                importance INTEGER DEFAULT 5,
                created_at TEXT,
                updated_at TEXT,
                access_count INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)

        # 对话历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT,
                session_id TEXT DEFAULT 'default'
            )
        """)

        conn.commit()
        conn.close()

    def add_memory(self, content, memory_type="general", importance=5, metadata=None):
        """添加记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO memories (content, memory_type, importance, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (content, memory_type, importance, now, now, json.dumps(metadata or {}, ensure_ascii=False)))

        conn.commit()
        memory_id = cursor.lastrowid
        conn.close()
        return memory_id

    def get_relevant_memories(self, query, limit=5):
        """获取相关记忆（简单关键词匹配）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 按重要性和最近访问排序
        cursor.execute("""
            SELECT content, memory_type, importance, access_count
            FROM memories
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        return [{"content": r[0], "type": r[1], "importance": r[2]} for r in results]

    def add_conversation(self, role, content, session_id="default"):
        """添加对话记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO conversations (role, content, timestamp, session_id)
            VALUES (?, ?, ?, ?)
        """, (role, content, now, session_id))

        conn.commit()
        conn.close()

    def get_recent_conversations(self, limit=10, session_id="default"):
        """获取最近对话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT role, content, timestamp
            FROM conversations
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (session_id, limit))

        results = cursor.fetchall()
        conn.close()
        return list(reversed(results))

    def get_stats(self):
        """获取记忆统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM memories")
        memory_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]

        conn.close()
        return {"memory_count": memory_count, "conversation_count": conv_count}

    def export_all(self):
        """导出所有数据（用于同步）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM memories")
        memories = cursor.fetchall()

        cursor.execute("SELECT * FROM conversations")
        conversations = cursor.fetchall()

        conn.close()
        return {"memories": memories, "conversations": conversations}

    def import_all(self, data):
        """导入数据（用于同步）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 清空并导入记忆
        cursor.execute("DELETE FROM memories")
        for row in data.get("memories", []):
            cursor.execute("""
                INSERT INTO memories (id, content, memory_type, importance, created_at, updated_at, access_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, row)

        # 清空并导入对话
        cursor.execute("DELETE FROM conversations")
        for row in data.get("conversations", []):
            cursor.execute("""
                INSERT INTO conversations (id, role, content, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?)
            """, row)

        conn.commit()
        conn.close()
