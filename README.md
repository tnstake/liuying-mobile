# 流萤手机版

一个可以安装在Android手机上的私人AI助理，与电脑端流萤数据无缝同步。

## 功能特性

- 🤖 **本地大模型**：支持 liuying:8b / qwen3:8b / qwen2.5:1.5b，离线可用
- ☁️ **云端模型路由**：复杂任务自动调用智谱 glm-4.7-flash（免费）
- 🧠 **记忆系统**：SQLite本地存储，短期/工作/长期记忆
- 🔄 **多端同步**：坚果云WebDAV同步，手机电脑数据无缝衔接
- 📱 **手机友好界面**：简约白色风格，触摸优化
- ⚡ **智能路由**：自动判断用本地小模型/大模型/云端模型

## 系统要求

- Android 7.0+
- 至少 4GB 内存（推荐 8GB+ 运行 8B 模型）
- Ollama Android 版（运行本地模型）

## 项目结构

```
liuying_mobile/
├── main.py              # 主程序（Kivy界面）
├── memory_system.py     # 记忆系统（SQLite）
├── cloud_router.py      # 云端模型路由
├── data_sync.py         # 数据同步（WebDAV）
├── config.json          # 配置文件
├── buildozer.spec       # Android打包配置
├── data/                # 数据目录
│   ├── memories.db      # 记忆数据库
│   └── config.json      # 运行时配置
└── assets/              # 资源文件
```

## 配置说明

### 1. 模型配置（config.json）

```json
{
  "default_model": "liuying:8b",
  "light_model": "qwen2.5:1.5b",
  "cloud_model": "glm-4.7-flash",
  "cloud_api_key": "你的智谱API密钥",
  "ollama_base_url": "http://127.0.0.1:11434"
}
```

### 2. 数据同步配置（坚果云）

1. 注册坚果云账号
2. 进入「账户信息」→「安全选项」→「添加应用」获取密码
3. 配置 WebDAV：

```json
{
  "sync": {
    "enabled": true,
    "webdav_url": "https://dav.jianguoyun.com/dav",
    "username": "你的坚果云邮箱",
    "password": "应用密码",
    "remote_path": "/liuying_sync",
    "auto_sync": true
  }
}
```

## 打包成APK

### 方法1：使用 Buildozer（推荐）

```bash
# 安装 buildozer
pip install buildozer

# 打包（需要Linux环境或WSL）
buildozer android debug
```

生成的APK在 `bin/` 目录下。

### 方法2：使用 Google Colab

1. 上传项目到 Google Drive
2. 在 Colab 中运行 buildozer 打包
3. 下载生成的APK

## 使用说明

### 首次使用

1. 安装并打开流萤App
2. 如果配置了同步，会自动从云端下载电脑端数据
3. 确保手机上已安装 Ollama 并下载了模型
4. 开始对话！

### 模型选择

- **简单对话**（"你好"、"谢谢"）：自动用 qwen2.5:1.5b（快速）
- **普通任务**：自动用 liuying:8b（本地大模型）
- **复杂任务**（写方案、分析、代码）：自动用云端 glm-4.7-flash（能力强）

### 数据同步

- 每次对话后自动上传到云端
- 每次启动App自动从云端下载最新数据
- 手机和电脑端数据完全一致

## 电脑端同步适配

在电脑端流萤中添加同步功能：

1. 复制 `data_sync.py` 到电脑端 `D:\4\core\` 目录
2. 在 `main_gui_pro.py` 中导入并初始化 DataSyncManager
3. 启动时调用 `sync_from_cloud()`，数据变更后调用 `sync_to_cloud()`

## 常见问题

**Q: 手机跑8B模型卡吗？**
A: Xiaomi 15（28GB内存）跑8B模型流畅，其他手机建议先用3B模型。

**Q: 没有网络能用吗？**
A: 可以！本地模型完全离线可用，只有复杂任务需要云端模型时才需要网络。

**Q: 数据安全吗？**
A: 所有数据存在本地SQLite，同步到坚果云是加密传输。你也可以关闭同步纯本地使用。

**Q: 能和电脑端流萤同时用吗？**
A: 可以！数据会自动同步，两端无缝衔接。建议不要同时修改同一数据。

## 版本历史

### v1.0.0
- 初始版本
- 本地模型聊天
- 记忆系统
- 云端模型路由
- WebDAV数据同步
- 手机友好界面
