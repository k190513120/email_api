#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from imap_email_test import IMAPEmailClient
import os
from dotenv import load_dotenv, find_dotenv

# 加载环境变量
load_dotenv(find_dotenv())

def test_email_attachments():
    """测试邮件附件提取功能"""
    client = IMAPEmailClient('imap.feishu.cn', 993, True)
    
    try:
        # 连接并登录
        email_user = 'miaomiao@basebitable.fun'
        email_password = 'poDq55NfdlKrPSEc'
        
        if not email_user or not email_password:
            print("缺少邮箱配置环境变量")
            return
            
        if not client.connect(email_user, email_password):
            print("连接失败")
            return
        
        # 选择收件箱
        if not client.select_folder('INBOX'):
            print("选择文件夹失败")
            return
        
        # 搜索邮件
        email_ids = client.search_emails('ALL', limit=5)
        
        print(f"\n=== 邮件附件检查结果 ===")
        print(f"共找到 {len(email_ids)} 封邮件")
        
        for i, email_id in enumerate(email_ids, 1):
            print(f"\n邮件 {i} (ID: {email_id}):")
            
            # 获取邮件详细内容
            email_info = client.get_email_content(email_id)
            if not email_info:
                print("  获取邮件内容失败")
                continue
                
            print(f"  主题: {email_info.get('subject', 'N/A')}")
            print(f"  发件人: {email_info.get('from', 'N/A')}")
            
            attachments = email_info.get('attachments', [])
            print(f"  附件数量: {len(attachments)}")
            
            if attachments:
                for j, attachment in enumerate(attachments, 1):
                    print(f"    附件 {j}:")
                    print(f"      文件名: {attachment.get('filename', 'N/A')}")
                    print(f"      大小: {attachment.get('size', 'N/A')} 字节")
                    print(f"      类型: {attachment.get('content_type', 'N/A')}")
                    print(f"      内容存在: {'是' if attachment.get('content') else '否'}")
            else:
                print("    无附件")
        
    except Exception as e:
        print(f"测试过程中出错: {e}")
    finally:
        if client.connected:
            client.disconnect()

if __name__ == "__main__":
    test_email_attachments()