#!/usr/bin/env python3
"""
调试模块导入问题的脚本
用于检查在不同Python版本下的模块导入情况
"""

import sys
import traceback
import os

print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"当前工作目录: {os.getcwd()}")
print(f"Python模块搜索路径:")
for path in sys.path:
    print(f"  - {path}")

print("\n=== 开始测试模块导入 ===")

# 测试抖音同步模块
print("\n1. 测试抖音同步模块导入:")
try:
    from douyin_sync_action import DouyinVideoSync
    print("✅ DouyinVideoSync 导入成功")
except ImportError as e:
    print(f"❌ DouyinVideoSync 导入失败: {e}")
    print(f"详细错误: {traceback.format_exc()}")
except Exception as e:
    print(f"❌ DouyinVideoSync 导入时发生其他错误: {e}")
    print(f"详细错误: {traceback.format_exc()}")

# 测试邮件同步模块
print("\n2. 测试邮件同步模块导入:")
try:
    from email_sync_action import EmailSyncAction
    print("✅ EmailSyncAction 导入成功")
except ImportError as e:
    print(f"❌ EmailSyncAction 导入失败: {e}")
    print(f"详细错误: {traceback.format_exc()}")
except Exception as e:
    print(f"❌ EmailSyncAction 导入时发生其他错误: {e}")
    print(f"详细错误: {traceback.format_exc()}")

# 测试标准库模块
print("\n3. 测试Python标准库模块:")
test_modules = [
    ('email', 'email'),
    ('email.mime', 'email.mime'),
    ('email.mime.text', 'email.mime.text'),
    ('imaplib', 'imaplib'),
    ('smtplib', 'smtplib'),
    ('cgi', 'cgi'),  # Python 3.13中已移除
]

for module_name, import_name in test_modules:
    try:
        __import__(import_name)
        print(f"✅ {module_name} 导入成功")
    except ImportError as e:
        print(f"❌ {module_name} 导入失败: {e}")
    except Exception as e:
        print(f"❌ {module_name} 导入时发生其他错误: {e}")

# 检查文件是否存在
print("\n4. 检查关键文件是否存在:")
files_to_check = [
    'douyin_sync_action.py',
    'email_sync_action.py',
    'imap_email_test.py',
    'requirements.txt'
]

for filename in files_to_check:
    if os.path.exists(filename):
        print(f"✅ {filename} 存在")
    else:
        print(f"❌ {filename} 不存在")

print("\n=== 调试完成 ===")