"""
流萤手机版 - 主程序
Xiaomi 15 适配，简约白色风格，触摸友好
"""
import os
import sys
import json
import time
import threading
from datetime import datetime

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

# 流萤核心模块
from memory_system import MemorySystem
from cloud_router import CloudModelRouter
from data_sync import DataSyncManager

# 配置
CONFIG = {
    "ollama_base_url": "http://127.0.0.1:11434",
    "default_model": "liuying:8b",
    "light_model": "qwen2.5:1.5b",
    "cloud_model": "glm-4.7-flash",
    "cloud_api_key": "",
    "cloud_base_url": "https://open.bigmodel.cn/api/paas/v4",
    "user_name": "take",
    "ai_name": "流萤",
    "data_dir": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"),
}

# 颜色定义（简约白色风格）
COLORS = {
    "bg": get_color_from_hex("#FFFFFF"),
    "bg_chat": get_color_from_hex("#F8F9FA"),
    "text": get_color_from_hex("#1A1B1C"),
    "text_secondary": get_color_from_hex("#6B7280"),
    "user_bubble": get_color_from_hex("#E3F2FD"),
    "ai_bubble": get_color_from_hex("#FFFFFF"),
    "ai_bubble_border": get_color_from_hex("#E5E7EB"),
    "accent": get_color_from_hex("#5B9BD5"),
    "input_bg": get_color_from_hex("#F3F4F6"),
    "border": get_color_from_hex("#E5E7EB"),
}


class MessageBubble(BoxLayout):
    """消息气泡组件"""
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.padding = [12, 8]
        self.spacing = 8

        if is_user:
            self.pos_hint = {"right": 1}
            bubble_color = COLORS["user_bubble"]
            text_color = COLORS["text"]
        else:
            self.pos_hint = {"left": 1}
            bubble_color = COLORS["ai_bubble"]
            text_color = COLORS["text"]

        # 气泡背景
        with self.canvas.before:
            Color(*bubble_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])
        self.bind(pos=self._update_rect, size=self._update_rect)

        # 消息文字
        self.label = Label(
            text=text,
            size_hint_y=None,
            halign="left" if not is_user else "right",
            valign="top",
            color=text_color,
            text_size=(Window.width * 0.7, None),
            padding=[8, 6],
        )
        self.label.bind(texture_size=self._on_texture_size)
        self.add_widget(self.label)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_texture_size(self, instance, value):
        self.height = max(value[1] + 16, 40)
        self.label.height = value[1]


class ChatArea(ScrollView):
    """聊天区域"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.do_scroll_x = False
        self.bar_width = 0

        self.chat_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8,
            padding=[12, 12],
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter("height"))
        self.add_widget(self.chat_layout)

    def add_message(self, text, is_user=False):
        bubble = MessageBubble(text=text, is_user=is_user)
        self.chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: self.scroll_to_bottom(), 0.1)

    def scroll_to_bottom(self):
        self.scroll_y = 0


class TopBar(BoxLayout):
    """顶部状态栏"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 48
        self.padding = [16, 8]
        self.spacing = 8

        with self.canvas.before:
            Color(*COLORS["bg"])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # AI名称
        self.name_label = Label(
            text="流萤",
            size_hint_x=0.3,
            halign="left",
            valign="middle",
            color=COLORS["text"],
            bold=True,
            font_size=16,
        )
        self.add_widget(self.name_label)

        # 状态
        self.status_label = Label(
            text="● 在线",
            size_hint_x=0.4,
            halign="center",
            valign="middle",
            color=COLORS["text_secondary"],
            font_size=12,
        )
        self.add_widget(self.status_label)

        # 模型
        self.model_label = Label(
            text=CONFIG["default_model"],
            size_hint_x=0.3,
            halign="right",
            valign="middle",
            color=COLORS["accent"],
            font_size=11,
        )
        self.add_widget(self.model_label)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def update_status(self, status, model=None):
        self.status_label.text = status
        if model:
            self.model_label.text = model


class InputArea(BoxLayout):
    """底部输入区域"""
    def __init__(self, on_send=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = 56
        self.padding = [12, 8]
        self.spacing = 8

        with self.canvas.before:
            Color(*COLORS["bg"])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.on_send = on_send

        # 输入框
        self.input = TextInput(
            hint_text="输入消息...",
            size_hint_x=0.85,
            background_color=COLORS["input_bg"],
            foreground_color=COLORS["text"],
            cursor_color=COLORS["accent"],
            padding=[12, 10],
            font_size=14,
            multiline=False,
        )
        self.input.bind(on_text_validate=self._on_enter)
        self.add_widget(self.input)

        # 发送按钮
        self.send_btn = Button(
            text="发送",
            size_hint_x=0.15,
            background_color=COLORS["accent"],
            color=(1, 1, 1, 1),
            bold=True,
            font_size=13,
        )
        self.send_btn.bind(on_press=self._on_send)
        self.add_widget(self.send_btn)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def _on_enter(self, instance):
        self._on_send(None)

    def _on_send(self, instance):
        text = self.input.text.strip()
        if text and self.on_send:
            self.on_send(text)
            self.input.text = ""

    def set_enabled(self, enabled):
        self.input.disabled = not enabled
        self.send_btn.disabled = not enabled


class LiuyingMobileApp(App):
    """流萤手机版主应用"""
    def build(self):
        Window.clearcolor = COLORS["bg_chat"]

        # 初始化核心系统
        self.memory = MemorySystem()
        self.cloud_router = CloudModelRouter(
            api_key=CONFIG.get("cloud_api_key", ""),
            base_url=CONFIG.get("cloud_base_url", "https://open.bigmodel.cn/api/paas/v4")
        )
        self.sync_manager = DataSyncManager(CONFIG.get("sync", {}))

        # 主布局
        self.root = BoxLayout(orientation="vertical")

        # 顶部栏
        self.top_bar = TopBar()
        self.root.add_widget(self.top_bar)

        # 聊天区域
        self.chat_area = ChatArea()
        self.root.add_widget(self.chat_area)

        # 输入区域
        self.input_area = InputArea(on_send=self.on_send_message)
        self.root.add_widget(self.input_area)

        # 启动时自动同步（从云端下载）
        if self.sync_manager.is_enabled():
            threading.Thread(target=self._auto_sync_on_start, daemon=True).start()

        # 欢迎消息
        Clock.schedule_once(lambda dt: self._show_welcome(), 0.5)

        return self.root

    def _auto_sync_on_start(self):
        """启动时自动从云端同步数据"""
        result = self.sync_manager.sync_from_cloud()
        if result["success"]:
            Clock.schedule_once(lambda dt: self._show_sync_notification("数据同步完成"), 1)

    def _show_sync_notification(self, message):
        """显示同步通知"""
        self.top_bar.update_status(f"● {message}", CONFIG["default_model"])

    def _show_welcome(self):
        self.chat_area.add_message(
            f"先生，您好！我是流萤。\n有什么可以帮您的吗？",
            is_user=False
        )

    def on_send_message(self, text):
        """处理用户发送消息"""
        # 显示用户消息
        self.chat_area.add_message(text, is_user=True)

        # 禁用输入
        self.input_area.set_enabled(False)
        self.top_bar.update_status("● 思考中...", CONFIG["default_model"])

        # 异步调用模型
        threading.Thread(target=self._generate_response, args=(text,), daemon=True).start()

    def _generate_response(self, text):
        """调用模型生成回复（集成记忆+云端路由）"""
        try:
            import requests

            # 1. 检索相关记忆
            relevant_memories = self.memory.get_relevant_memories(text, limit=3)
            memory_context = "\n".join([f"- {m['content']}" for m in relevant_memories])

            # 2. 保存用户对话到记忆
            self.memory.add_conversation("user", text)

            # 3. 智能路由：判断用本地还是云端
            use_cloud = self.cloud_router.should_use_cloud(text) and self.cloud_router.is_available()

            if use_cloud:
                # 云端模型
                model = CONFIG["cloud_model"]
                messages = [
                    {"role": "system", "content": self._get_system_prompt(memory_context)},
                    {"role": "user", "content": text},
                ]
                reply, error = self.cloud_router.chat(messages)
                if error:
                    reply = f"云端模型调用失败，已切换到本地模型。\n错误: {error}"
                    use_cloud = False

            if not use_cloud:
                # 本地模型
                model = self._route_model(text)
                response = requests.post(
                    f"{CONFIG['ollama_base_url']}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": self._get_system_prompt(memory_context)},
                            {"role": "user", "content": text},
                        ],
                        "stream": False,
                    },
                    timeout=120,
                )

                if response.status_code == 200:
                    result = response.json()
                    reply = result.get("message", {}).get("content", "抱歉，我没有理解您的意思。")
                else:
                    reply = f"抱歉，模型调用失败（状态码: {response.status_code}）"

            # 4. 保存AI回复到记忆
            self.memory.add_conversation("assistant", reply)

            # 5. 异步同步到云端（如果启用）
            if self.sync_manager.is_enabled():
                threading.Thread(target=self._sync_to_cloud_async, daemon=True).start()

        except requests.exceptions.ConnectionError:
            reply = "抱歉，无法连接到本地模型服务。请确保Ollama已启动。"
        except Exception as e:
            reply = f"抱歉，发生错误：{str(e)}"

        # 在主线程更新UI
        Clock.schedule_once(lambda dt: self._show_response(reply, model), 0)

    def _sync_to_cloud_async(self):
        """异步同步数据到云端"""
        try:
            self.sync_manager.sync_to_cloud()
        except Exception:
            pass

    def _route_model(self, text):
        """智能路由：判断用哪个模型"""
        # 简单关键词判断
        simple_keywords = ["你好", "您好", "嗨", "hi", "hello", "谢谢", "再见", "在吗"]
        complex_keywords = ["写", "分析", "方案", "代码", "计算", "对比", "研究", "总结", "规划"]

        text_lower = text.lower()

        # 简单对话用小模型
        if any(kw in text_lower for kw in simple_keywords) and len(text) < 10:
            return CONFIG["light_model"]

        # 复杂任务用大模型
        if any(kw in text_lower for kw in complex_keywords) or len(text) > 20:
            return CONFIG["default_model"]

        return CONFIG["default_model"]

    def _get_system_prompt(self, memory_context=""):
        """获取系统提示词（集成记忆）"""
        prompt = f"""你是流萤，一个私人AI助理。
- 用户名字是{CONFIG['user_name']}，称呼他为"先生"
- 回复简洁、直接、有礼貌
- 用中文回复
- 当前时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}"""

        if memory_context:
            prompt += f"\n\n【相关记忆】\n{memory_context}"

        return prompt

    def _show_response(self, reply, model):
        """显示AI回复"""
        self.chat_area.add_message(reply, is_user=False)
        self.input_area.set_enabled(True)
        self.top_bar.update_status("● 在线", model)


if __name__ == "__main__":
    LiuyingMobileApp().run()
