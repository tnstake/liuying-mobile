"""
流萤手机版 - 云端模型路由
复杂任务自动调用智谱glm-4.7-flash（免费）
"""
import json
import requests
from datetime import datetime


class CloudModelRouter:
    def __init__(self, api_key="", base_url="https://open.bigmodel.cn/api/paas/v4"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = "glm-4.7-flash"
        self.call_count = 0
        self.last_error = None

    def is_available(self):
        """检查云端模型是否可用"""
        return bool(self.api_key)

    def should_use_cloud(self, text):
        """判断是否应该用云端模型"""
        # 复杂任务关键词
        complex_keywords = [
            "写", "分析", "方案", "代码", "计算", "对比", "研究",
            "总结", "规划", "设计", "翻译", "编程", "debug",
            "算法", "架构", "优化", "报告", "论文", "文档"
        ]

        text_lower = text.lower()

        # 长文本或复杂任务用云端
        if len(text) > 30:
            return True

        if any(kw in text_lower for kw in complex_keywords):
            return True

        return False

    def chat(self, messages, temperature=0.7, max_tokens=2048):
        """调用云端模型"""
        if not self.api_key:
            return None, "未配置云端API密钥"

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                self.call_count += 1
                return content, None
            else:
                error = f"HTTP {response.status_code}: {response.text}"
                self.last_error = error
                return None, error

        except Exception as e:
            error = str(e)
            self.last_error = error
            return None, error

    def get_stats(self):
        """获取统计信息"""
        return {
            "model": self.model,
            "call_count": self.call_count,
            "available": self.is_available(),
            "last_error": self.last_error,
        }
