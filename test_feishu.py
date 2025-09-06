#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书邮箱IMAP连接测试脚本
使用提供的飞书邮箱配置进行连接测试
"""

from imap_email_test import IMAPEmailClient
import json

def test_feishu_imap():
    """
    测试飞书邮箱IMAP连接
    """
    print("=== 飞书邮箱IMAP连接测试 ===")
    
    # 飞书邮箱配置
    server = "imap.feishu.cn"
    port = 993
    use_ssl = True
    username = "miaomiao@basebitable.fun"
    password = "poDq55NfdlKrPSEc"
    
    print(f"服务器: {server}:{port}")
    print(f"用户名: {username}")
    print(f"使用SSL: {use_ssl}")
    print()
    
    # 创建IMAP客户端
    client = IMAPEmailClient(server, port, use_ssl)
    
    try:
        # 测试连接
        print("正在测试连接...")
        if not client.connect(username, password):
            print("连接失败！")
            return False
        
        print("连接成功！")
        
        # 列出文件夹
        print("\n=== 邮箱文件夹列表 ===")
        folders = client.list_folders()
        if folders:
            for i, folder in enumerate(folders[:10], 1):  # 只显示前10个
                print(f"{i}. {folder}")
        else:
            print("未找到文件夹")
        
        # 选择收件箱
        print("\n=== 选择收件箱 ===")
        if client.select_folder('INBOX'):
            # 搜索邮件
            print("\n=== 搜索最新邮件 ===")
            email_ids = client.search_emails('ALL', limit=5)
            
            if email_ids:
                print(f"找到 {len(email_ids)} 封邮件")
                
                # 获取第一封邮件详情
                if email_ids:
                    print("\n=== 第一封邮件详情 ===")
                    email_info = client.get_email_content(email_ids[0])
                    
                    if email_info:
                        print(f"邮件ID: {email_info['id']}")
                        print(f"主题: {email_info['subject']}")
                        print(f"发件人: {email_info['from']}")
                        print(f"收件人: {email_info['to']}")
                        print(f"日期: {email_info['date']}")
                        print(f"正文预览: {email_info['body'][:200]}...")
                        
                        # 保存测试结果
                        test_result = {
                            "test_time": "2025-01-07",
                            "server": server,
                            "port": port,
                            "username": username,
                            "connection_status": "成功",
                            "folders_count": len(folders) if folders else 0,
                            "emails_found": len(email_ids),
                            "sample_email": email_info
                        }
                        
                        with open('/Users/lanlan/Downloads/python快递/feishu_test_result.json', 'w', encoding='utf-8') as f:
                            json.dump(test_result, f, ensure_ascii=False, indent=2)
                        
                        print("\n测试结果已保存到 feishu_test_result.json")
                    else:
                        print("获取邮件详情失败")
            else:
                print("未找到邮件")
        else:
            print("选择收件箱失败")
        
        return True
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        return False
    
    finally:
        # 断开连接
        client.disconnect()
        print("\n测试完成")

if __name__ == "__main__":
    success = test_feishu_imap()
    if success:
        print("\n✅ 飞书邮箱IMAP连接测试成功！")
    else:
        print("\n❌ 飞书邮箱IMAP连接测试失败！")