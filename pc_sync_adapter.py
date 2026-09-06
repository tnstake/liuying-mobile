"""
电脑端流萤同步适配脚本
在电脑端main_gui_pro.py中添加数据同步功能
使用方法：运行此脚本，自动修改main_gui_pro.py添加同步功能
"""
import re
import shutil
from pathlib import Path

CORE_DIR = Path(r"D:\4\core")
MAIN_FILE = CORE_DIR / "main_gui_pro.py"
BACKUP_FILE = CORE_DIR / "main_gui_pro.py.bak_sync"
SYNC_FILE = Path(r"D:\4\liuying_mobile\data_sync.py")


def backup_main_file():
    """备份主程序"""
    shutil.copy2(MAIN_FILE, BACKUP_FILE)
    print(f"✅ 已备份主程序到: {BACKUP_FILE}")


def copy_sync_module():
    """复制同步模块到core目录"""
    dest = CORE_DIR / "data_sync.py"
    shutil.copy2(SYNC_FILE, dest)
    print(f"✅ 已复制 data_sync.py 到: {dest}")


def add_import(content):
    """添加导入语句"""
    import_line = "from data_sync import DataSyncManager"
    if import_line not in content:
        # 在其他导入之后添加
        pattern = r"(from config import.*\n)"
        match = re.search(pattern, content)
        if match:
            content = content[:match.end()] + import_line + "\n" + content[match.end():]
            print("✅ 已添加 DataSyncManager 导入")
        else:
            print("⚠️ 未找到导入位置，请手动添加导入")
    return content


def add_init(content):
    """在__init__中添加同步管理器初始化"""
    init_code = """
        # 数据同步管理器
        try:
            self.sync_manager = DataSyncManager(self.config.get('sync', {}))
            print("[数据同步] 同步管理器已初始化" + ("（已启用）" if self.sync_manager.is_enabled() else "（未启用）"))
        except Exception as e:
            self.sync_manager = None
            print(f"[数据同步] 初始化失败: {e}")
"""
    if "self.sync_manager" not in content:
        # 在self.config初始化之后添加
        pattern = r"(self\.config\s*=.*\n)"
        match = re.search(pattern, content)
        if match:
            content = content[:match.end()] + init_code + content[match.end():]
            print("✅ 已添加同步管理器初始化")
        else:
            print("⚠️ 未找到初始化位置，请手动添加")
    return content


def add_startup_sync(content):
    """添加启动时同步"""
    startup_code = """
        # 启动时从云端同步数据
        if hasattr(self, 'sync_manager') and self.sync_manager and self.sync_manager.is_enabled():
            def _sync_on_start():
                try:
                    result = self.sync_manager.sync_from_cloud()
                    if result['success']:
                        print(f"[数据同步] 启动同步完成，下载了{result['files_downloaded']}个文件")
                except Exception as e:
                    print(f"[数据同步] 启动同步失败: {e}")
            threading.Thread(target=_sync_on_start, daemon=True).start()
"""
    if "_sync_on_start" not in content:
        # 在GUI初始化之后添加
        pattern = r"(self\.protocol\(.*\).*\n)"
        match = re.search(pattern, content)
        if match:
            content = content[:match.end()] + startup_code + content[match.end():]
            print("✅ 已添加启动时同步")
        else:
            print("⚠️ 未找到启动位置，请手动添加")
    return content


def add_sync_after_message(content):
    """在消息处理后添加同步"""
    sync_code = """
            # 对话后同步到云端
            if hasattr(self, 'sync_manager') and self.sync_manager and self.sync_manager.is_enabled():
                def _sync_after_chat():
                    try:
                        self.sync_manager.sync_to_cloud()
                    except Exception:
                        pass
                threading.Thread(target=_sync_after_chat, daemon=True).start()
"""
    if "_sync_after_chat" not in content:
        # 在保存对话历史之后添加
        pattern = r"(self\.save_chat_history\(\).*\n)"
        match = re.search(pattern, content)
        if match:
            content = content[:match.end()] + sync_code + content[match.end():]
            print("✅ 已添加对话后同步")
        else:
            print("⚠️ 未找到保存对话位置，请手动添加")
    return content


def main():
    print("=" * 60)
    print("🔧 电脑端流萤同步适配脚本")
    print("=" * 60)

    # 1. 备份
    backup_main_file()

    # 2. 复制同步模块
    copy_sync_module()

    # 3. 读取主程序
    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 4. 添加导入
    content = add_import(content)

    # 5. 添加初始化
    content = add_init(content)

    # 6. 添加启动同步
    content = add_startup_sync(content)

    # 7. 添加对话后同步
    content = add_sync_after_message(content)

    # 8. 保存修改
    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("\n" + "=" * 60)
    print("✅ 电脑端同步适配完成！")
    print("=" * 60)
    print("\n📝 下一步：")
    print("1. 在 config.json 中添加同步配置：")
    print('   "sync": {')
    print('     "enabled": true,')
    print('     "webdav_url": "https://dav.jianguoyun.com/dav",')
    print('     "username": "你的坚果云邮箱",')
    print('     "password": "应用密码",')
    print('     "remote_path": "/liuying_sync"')
    print('   }')
    print("2. 重启流萤，启动时会自动从云端同步数据")
    print("3. 每次对话后会自动同步到云端")
    print("\n⚠️  如果启动失败，可以从备份恢复：")
    print(f"   复制 {BACKUP_FILE} 到 {MAIN_FILE}")


if __name__ == "__main__":
    main()
