# 流萤 Termux版 使用说明

## 📱 这是什么？

流萤的Android Termux命令行版本，可以在手机上直接运行，**不需要电脑，不需要打包APK**，安装后立刻就能用。

## ✨ 功能特性

- ✅ **本地模型**：支持手机本地Ollama运行（完全离线）
- ✅ **云端模型**：支持智谱GLM-4.7-Flash（免费，需要API Key）
- ✅ **智能路由**：自动判断用本地还是云端模型
- ✅ **记忆系统**：SQLite记忆，记住你的偏好和历史
- ✅ **对话历史**：自动保存对话，重启不丢失
- ✅ **命令系统**：/help、/memory、/save等实用命令

## 🚀 快速开始（5分钟搞定）

### 第1步：安装Termux

1. 打开手机浏览器，访问 **https://f-droid.org/packages/com.termux/**
2. 下载并安装Termux（F-Droid版本，不要用Google Play版本，已停止更新）
3. 打开Termux

### 第2步：把流萤文件传到手机

有两种方式：

**方式A：用手机直接下载（推荐）**
1. 在手机浏览器打开你的GitHub仓库：https://github.com/tnstake/liuying-mobile
2. 点绿色的「Code」按钮 → 「Download ZIP」
3. 下载后解压到手机存储

**方式B：用电脑传文件**
1. 把 `liuying_termux` 文件夹复制到手机
2. 记住放在哪个目录（比如 `Download/liuying_termux`）

### 第3步：在Termux里安装

1. 打开Termux，运行以下命令（复制粘贴，一行一行来）：

```bash
# 授予存储权限
termux-setup-storage
# （会弹出权限请求，点"允许"）

# 进入流萤目录（根据你实际放的位置调整路径）
cd ~/storage/downloads/liuying_termux

# 运行安装脚本
bash install.sh
```

2. 等待安装完成（大约2-3分钟）

### 第4步：配置云端API Key（推荐，立刻能用）

1. 用文本编辑器打开 `config.json`
2. 找到 `"api_key": "在这里填写你的智谱API Key"`
3. 把引号里的内容换成你的智谱API Key
   - 没有API Key？去 https://open.bigmodel.cn/ 注册，免费额度够用
4. 保存文件

### 第5步：启动流萤

```bash
bash ~/liuying.sh
```

或者：
```bash
cd ~/liuying_termux
python main.py
```

## 🎮 使用命令

| 命令 | 功能 |
|------|------|
| `/help` | 显示帮助 |
| `/model` | 查看模型状态 |
| `/memory` | 查看记忆数量 |
| `/save 内容` | 保存重要信息到记忆 |
| `/clear` | 清空当前对话历史 |
| `/config` | 查看配置文件路径 |
| `/quit` | 退出流萤 |

## 🤖 模型配置

### 只用云端模型（推荐，最简单）

1. 在 `config.json` 里填好智谱API Key
2. 确保 `"use_cloud": true`
3. 启动流萤，直接用！

### 用本地模型（完全离线）

1. 在手机上安装 **Ollama Android版**
   - 下载地址：https://ollama.com/download/android
2. 打开Ollama，下载模型：
   ```bash
   ollama pull qwen2.5:1.5b
   ```
3. 在 `config.json` 里把 `"use_cloud": false`
4. 启动流萤

### 混合模式（智能切换）

1. 同时配置云端API Key和本地Ollama
2. `"use_cloud": true`
3. 流萤会自动判断：
   - 简单对话 → 用本地模型（快、省流量）
   - 复杂任务 → 用云端模型（更聪明）

## ⚙️ 配置说明

编辑 `config.json`：

```json
{
  "model": {
    "local_model": "qwen2.5:1.5b",      // 本地模型名称
    "cloud_model": "glm-4.7-flash",       // 云端模型名称
    "use_cloud": true,                      // 是否启用云端模型
    "ollama_url": "http://127.0.0.1:11434" // Ollama地址
  },
  "cloud_api": {
    "api_key": "你的API Key",               // 智谱API Key
    "max_tokens": 2048,                     // 最大回复长度
    "temperature": 0.7                       // 创造性（0-1）
  },
  "system_prompt": "你是流萤..."            // 系统提示词（流萤的人设）
}
```

## ❓ 常见问题

**Q: 安装时提示权限错误？**
A: 先运行 `termux-setup-storage`，然后点"允许"。

**Q: 提示"没有可用的模型"？**
A: 要么配置云端API Key，要么安装本地Ollama。推荐先用云端，最简单。

**Q: 怎么更新流萤？**
A: 重新下载最新版本，覆盖 `liuying_termux` 文件夹即可（记忆文件不会丢）。

**Q: 记忆存在哪里？**
A: 在 `liuying_termux/liuying_memory.db`，是SQLite数据库文件。

**Q: 可以和电脑端同步记忆吗？**
A: 可以！把 `liuying_memory.db` 文件复制到电脑端流萤目录即可。

## 📞 遇到问题？

1. 先看上面的常见问题
2. 检查 `config.json` 配置是否正确
3. 确保网络连接正常（用云端模型时）

---

**享受你的随身AI助手吧！** 🎉
