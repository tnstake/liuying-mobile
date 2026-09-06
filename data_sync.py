"""
流萤手机版 - 数据同步模块
支持坚果云WebDAV同步，多端数据无缝衔接
"""
import os
import json
import time
import base64
import requests
from datetime import datetime
from pathlib import Path


class DataSyncManager:
    def __init__(self, config=None):
        self.config = config or {}
        self.webdav_url = self.config.get("webdav_url", "")
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.remote_path = self.config.get("remote_path", "/liuying_sync")
        self.local_data_dir = Path(__file__).parent / "data"
        self.last_sync_time = None
        self.sync_enabled = bool(self.webdav_url and self.username and self.password)

    def _get_auth_header(self):
        """获取WebDAV认证头"""
        auth = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {auth}"}

    def is_enabled(self):
        """检查同步是否启用"""
        return self.sync_enabled

    def upload_file(self, local_path, remote_filename):
        """上传文件到WebDAV"""
        if not self.sync_enabled:
            return False, "同步未启用"

        try:
            with open(local_path, "rb") as f:
                content = f.read()

            url = f"{self.webdav_url}{self.remote_path}/{remote_filename}"
            response = requests.put(url, data=content, headers=self._get_auth_header(), timeout=30)

            if response.status_code in [200, 201, 204]:
                return True, "上传成功"
            else:
                return False, f"上传失败: HTTP {response.status_code}"

        except Exception as e:
            return False, f"上传异常: {str(e)}"

    def download_file(self, remote_filename, local_path):
        """从WebDAV下载文件"""
        if not self.sync_enabled:
            return False, "同步未启用"

        try:
            url = f"{self.webdav_url}{self.remote_path}/{remote_filename}"
            response = requests.get(url, headers=self._get_auth_header(), timeout=30)

            if response.status_code == 200:
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(response.content)
                return True, "下载成功"
            else:
                return False, f"下载失败: HTTP {response.status_code}"

        except Exception as e:
            return False, f"下载异常: {str(e)}"

    def sync_to_cloud(self):
        """同步本地数据到云端（上传）"""
        if not self.sync_enabled:
            return {"success": False, "message": "同步未启用", "files_uploaded": 0}

        files_uploaded = 0
        errors = []

        # 需要同步的文件
        sync_files = [
            "memories.db",
            "config.json",
            "goals.db",
            "optimization.db",
        ]

        for filename in sync_files:
            local_path = self.local_data_dir / filename
            if local_path.exists():
                success, msg = self.upload_file(str(local_path), filename)
                if success:
                    files_uploaded += 1
                else:
                    errors.append(f"{filename}: {msg}")

        self.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "success": len(errors) == 0,
            "files_uploaded": files_uploaded,
            "errors": errors,
            "sync_time": self.last_sync_time,
        }

    def sync_from_cloud(self):
        """从云端同步数据到本地（下载）"""
        if not self.sync_enabled:
            return {"success": False, "message": "同步未启用", "files_downloaded": 0}

        files_downloaded = 0
        errors = []

        sync_files = [
            "memories.db",
            "config.json",
            "goals.db",
            "optimization.db",
        ]

        for filename in sync_files:
            local_path = self.local_data_dir / filename
            success, msg = self.download_file(filename, str(local_path))
            if success:
                files_downloaded += 1
            else:
                errors.append(f"{filename}: {msg}")

        self.last_sync_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "success": len(errors) == 0,
            "files_downloaded": files_downloaded,
            "errors": errors,
            "sync_time": self.last_sync_time,
        }

    def get_sync_status(self):
        """获取同步状态"""
        return {
            "enabled": self.sync_enabled,
            "last_sync": self.last_sync_time,
            "webdav_url": self.webdav_url,
            "remote_path": self.remote_path,
        }

    def configure(self, webdav_url, username, password, remote_path="/liuying_sync"):
        """配置同步参数"""
        self.webdav_url = webdav_url
        self.username = username
        self.password = password
        self.remote_path = remote_path
        self.sync_enabled = bool(webdav_url and username and password)
        return self.sync_enabled
