#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件同步功能测试脚本
用于验证邮件同步到飞书多维表格的完整流程
"""

import os
import sys
from email_sync_action import EmailSyncAction

def test_email_sync():
    """测试邮件同步功能"""
    print("=== 邮件同步功能测试 ===")
    
    # 检查必要的环境变量
    required_vars = [
        'EMAIL_USERNAME',
        'EMAIL_PASSWORD', 
        'EMAIL_PROVIDER',
        'BITABLE_URL',
        'PERSONAL_BASE_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        return False
    
    try:
        # 创建同步实例
        sync_action = EmailSyncAction()
        
        # 测试邮箱连接
        print("\n1. 测试邮箱连接...")
        emails = sync_action.get_emails_from_imap()
        print(f"✅ 邮箱连接成功，获取到 {len(emails)} 封邮件")
        
        if emails:
            # 测试飞书同步
            print("\n2. 测试飞书多维表格同步...")
            result = sync_action.sync_to_feishu_bitable(emails)
            
            if result.get('success'):
                print(f"✅ 飞书同步成功，同步了 {result.get('synced_count', 0)} 条记录")
            else:
                print(f"❌ 飞书同步失败: {result.get('message', '未知错误')}")
                return False
        else:
            print("⚠️  没有找到邮件，跳过同步测试")
        
        print("\n✅ 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主函数"""
    success = test_email_sync()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()