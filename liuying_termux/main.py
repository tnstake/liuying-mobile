#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流萤手机版 - Termux命令行版本
适用于Android Termux环境，支持本地Ollama + 云端智谱模型
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

# 加载配置
def load_config():
    default_config = {
        "model": {
            "local_model": "qwen2.5:1.5b",
            "cloud_model": "glm-4.7-flash",
            "use_cloud": True,
            "ollama_url": "http://127.0.0.1:11434"
        },
        "cloud_api": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "api_key": "",
            "max_tokens": 2048,
            "temperature": 0.7
        },
        "memory": {
            "enabled": True,
            "db_path": "liuying_memory.db"
        },
        "system_prompt": "你是流萤，一个聪明、温柔、乐于助人的AI助手。请用简洁、自然的方式回答用户的问题。称呼用户为'先生'。"
    }
    
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            # 合并配置
            for key in default_config:
                if key in user_config:
                    if isinstance(default_config[key], dict) and isinstance(user_config[key], dict):
                        default_config[key].update(user_config[key])
                    else:
                        default_config[key] = user_config[key]
        except Exception as e:
            print(f"⚠️  配置文件读取失败: {e}，使用默认配置")
    
    return default_config

# 记忆系统
class MemorySystem:
    def __init__(self, db_path="liuying_memory.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        try:
            import sqlite3
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"⚠️  记忆系统初始化失败: {e}")
    
    def add_memory(self, content, memory_type="general"):
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO memories (content, type) VALUES (?, ?)", (content, memory_type))
            self.conn.commit()
        except Exception as e:
            print(f"⚠️  记忆写入失败: {e}")
    
    def get_relevant_memories(self, query, limit=3):
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            # 简单的关键词匹配
            keywords = query.split()
            placeholders = ' OR '.join(['content LIKE ?' for _ in keywords])
            params = [f'%{kw}%' for kw in keywords]
            cursor.execute(f"SELECT content FROM memories WHERE {placeholders} ORDER BY created_at DESC LIMIT ?", params + [limit])
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            return []
    
    def add_conversation(self, role, content):
        if not self.conn:
            return
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO conversations (role, content) VALUES (?, ?)", (role, content))
            self.conn.commit()
        except Exception as e:
            pass
    
    def get_recent_conversations(self, limit=10):
        if not self.conn:
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT role, content FROM conversations ORDER BY id DESC LIMIT ?", (limit,))
            return cursor.fetchall()[::-1]  # 反转顺序，最早的在前
        except Exception as e:
            return []
    
    def close(self):
        if self.conn:
            self.conn.close()

# 本地Ollama模型
class LocalModel:
    def __init__(self, config):
        self.base_url = config['model']['ollama_url']
        self.model = config['model']['local_model']
    
    def is_available(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def chat(self, messages, temperature=0.7):
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature}
                },
                timeout=60
            )
            if response.status_code == 200:
                return response.json()['message']['content']
            else:
                return f"⚠️  本地模型返回错误: {response.status_code}"
        except requests.exceptions.Timeout:
            return "⚠️  本地模型响应超时"
        except Exception as e:
            return f"⚠️  本地模型调用失败: {str(e)}"

# 云端智谱模型
class CloudModel:
    def __init__(self, config):
        self.base_url = config['cloud_api']['base_url']
        self.api_key = config['cloud_api']['api_key']
        self.model = config['model']['cloud_model']
        self.max_tokens = config['cloud_api']['max_tokens']
        self.temperature = config['cloud_api']['temperature']
    
    def is_available(self):
        return bool(self.api_key)
    
    def chat(self, messages, temperature=None):
        if not self.api_key:
            return "⚠️  云端模型未配置API Key，请在config.json中填写智谱API Key"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": temperature if temperature else self.temperature
            }
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"⚠️  云端模型返回错误: {response.status_code} - {response.text[:200]}"
        except requests.exceptions.Timeout:
            return "⚠️  云端模型响应超时"
        except Exception as e:
            return f"⚠️  云端模型调用失败: {str(e)}"

# 流萤主类
class Liuying:
    def __init__(self):
        self.config = load_config()
        self.memory = MemorySystem(self.config['memory']['db_path']) if self.config['memory']['enabled'] else None
        self.local_model = LocalModel(self.config)
        self.cloud_model = CloudModel(self.config)
        self.conversation_history = []
        
        # 加载历史对话
        if self.memory:
            for role, content in self.memory.get_recent_conversations(20):
                self.conversation_history.append({"role": role, "content": content})
    
    def get_system_prompt(self):
        return self.config['system_prompt']
    
    def should_use_cloud(self, user_input):
        """判断是否应该使用云端模型"""
        if not self.config['model']['use_cloud'] or not self.cloud_model.is_available():
            return False
        
        # 复杂任务用云端
        complex_keywords = ['写', '分析', '研究', '方案', '代码', '编程', '翻译', '总结', '对比', '设计', '规划']
        if any(kw in user_input for kw in complex_keywords):
            return True
        
        # 长输入用云端
        if len(user_input) > 50:
            return True
        
        return False
    
    def chat(self, user_input):
        # 记录用户输入
        if self.memory:
            self.memory.add_conversation("user", user_input)
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # 构建消息
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        
        # 加入相关记忆
        if self.memory:
            relevant_memories = self.memory.get_relevant_memories(user_input)
            if relevant_memories:
                memory_context = "相关记忆:\n" + "\n".join([f"- {m}" for m in relevant_memories])
                messages.append({"role": "system", "content": memory_context})
        
        # 加入历史对话（最近10轮）
        messages.extend(self.conversation_history[-10:])
        
        # 选择模型
        use_cloud = self.should_use_cloud(user_input)
        model_name = "云端" if use_cloud else "本地"
        
        print(f"\n🤖 流萤正在思考（{model_name}模型）...")
        
        # 调用模型
        if use_cloud:
            response = self.cloud_model.chat(messages)
        else:
            if self.local_model.is_available():
                response = self.local_model.chat(messages)
            else:
                # 本地模型不可用，尝试云端
                if self.cloud_model.is_available():
                    print("⚠️  本地模型不可用，切换到云端模型")
                    response = self.cloud_model.chat(messages)
                else:
                    response = "⚠️  没有可用的模型。请启动本地Ollama，或在config.json中配置云端API Key。"
        
        # 记录助手回复
        if self.memory:
            self.memory.add_conversation("assistant", response)
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def save_memory(self, content):
        """保存重要信息到记忆"""
        if self.memory:
            self.memory.add_memory(content)
            print("✅ 已保存到记忆")
        else:
            print("⚠️  记忆系统未启用")
    
    def show_help(self):
        print("""
📖 流萤命令帮助:
  /help     - 显示帮助
  /memory   - 查看记忆数量
  /clear    - 清空当前对话历史
  /save [内容] - 保存重要信息到记忆
  /model    - 查看当前模型状态
  /config   - 打开配置文件
  /quit     - 退出流萤
        """)
    
    def show_model_status(self):
        local_available = self.local_model.is_available()
        cloud_available = self.cloud_model.is_available()
        print(f"""
🤖 模型状态:
  本地模型 ({self.config['model']['local_model']}): {'✅ 可用' if local_available else '❌ 不可用'}
  云端模型 ({self.config['model']['cloud_model']}): {'✅ 已配置' if cloud_available else '⚠️  未配置API Key'}
  Ollama地址: {self.config['model']['ollama_url']}
        """)

def print_banner():
    print("""
╔══════════════════════════════════════╗
║       ⚡ 流萤 v3.0.0 (Termux版)      ║
║       本地AI助手 · 随时随地可用        ║
╠══════════════════════════════════════╣
║  输入 /help 查看帮助                   ║
║  输入 /quit 退出                       ║
╚══════════════════════════════════════╝
    """)

def main():
    print_banner()
    
    liuying = Liuying()
    
    # 显示模型状态
    liuying.show_model_status()
    
    print("先生，您好！有什么可以帮您的吗？\n")
    
    while True:
        try:
            user_input = input("👤 先生: ").strip()
            
            if not user_input:
                continue
            
            # 命令处理
            if user_input.startswith('/'):
                if user_input == '/help' or user_input == '/?':
                    liuying.show_help()
                elif user_input == '/quit' or user_input == '/exit':
                    print("\n👋 先生，再见！流萤随时为您服务。")
                    if liuying.memory:
                        liuying.memory.close()
                    break
                elif user_input == '/clear':
                    liuying.conversation_history = []
                    print("✅ 对话历史已清空")
                elif user_input == '/model':
                    liuying.show_model_status()
                elif user_input == '/memory':
                    if liuying.memory:
                        try:
                            cursor = liuying.memory.conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM memories")
                            count = cursor.fetchone()[0]
                            print(f"📚 当前记忆数量: {count} 条")
                        except:
                            print("📚 记忆系统运行中")
                    else:
                        print("⚠️  记忆系统未启用")
                elif user_input.startswith('/save '):
                    content = user_input[6:].strip()
                    if content:
                        liuying.save_memory(content)
                    else:
                        print("⚠️  请输入要保存的内容")
                elif user_input == '/config':
                    print(f"📝 配置文件路径: {CONFIG_PATH}")
                    print("请用文本编辑器打开修改配置")
                else:
                    print(f"⚠️  未知命令: {user_input}，输入 /help 查看帮助")
                continue
            
            # 正常对话
            response = liuying.chat(user_input)
            print(f"\n🧚 流萤: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 先生，再见！流萤随时为您服务。")
            if liuying.memory:
                liuying.memory.close()
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print("请重试或输入 /help 查看帮助\n")

if __name__ == "__main__":
    main()
