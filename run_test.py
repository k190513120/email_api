#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的IMAP邮箱测试运行脚本
提供快速测试功能，无需交互式输入
"""

import json
import os
from imap_email_test import IMAPEmailClient

def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 配置信息
    """
    config_path = '/Users/lanlan/Downloads/python快递/config.json'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"配置文件 {config_path} 不存在")
        return None
    except json.JSONDecodeError:
        print("配置文件格式错误")
        return None

def quick_test():
    """
    快速测试函数
    使用预设配置进行测试
    """
    print("=== IMAP邮箱快速测试 ===")
    
    # 加载配置
    config = load_config()
    if not config:
        return False
    
    # 提示用户输入测试信息
    print("\n请输入测试信息:")
    provider = input("邮箱服务商 (gmail/qq/163/126/outlook等): ").lower().strip()
    username = input("邮箱用户名: ").strip()
    password = input("邮箱密码或授权码: ").strip()
    
    if not all([provider, username, password]):
        print("输入信息不完整")
        return False
    
    # 获取服务器配置
    if provider not in config['email_servers']:
        print(f"不支持的邮箱服务商: {provider}")
        print(f"支持的服务商: {', '.join(config['email_servers'].keys())}")
        return False
    
    server_config = config['email_servers'][provider]
    print(f"\n使用配置: {server_config['description']}")
    print(f"服务器: {server_config['server']}:{server_config['port']}")
    
    # 创建客户端并测试连接
    client = IMAPEmailClient(
        server_config['server'],
        server_config['port'],
        server_config['ssl']
    )
    
    try:
        # 连接测试
        print("\n=== 连接测试 ===")
        if not client.connect(username, password):
            return False
        
        # 文件夹测试
        print("\n=== 文件夹列表 ===")
        folders = client.list_folders()
        print(f"共找到 {len(folders)} 个文件夹")
        
        # 选择收件箱
        if client.select_folder('INBOX'):
            # 邮件数量测试
            print("\n=== 邮件获取测试 ===")
            email_ids = client.search_emails('ALL', limit=3)
            
            if email_ids:
                print(f"获取到 {len(email_ids)} 封邮件")
                
                # 获取第一封邮件详情
                email_info = client.get_email_content(email_ids[0])
                if email_info:
                    print("\n=== 邮件解析测试 ===")
                    print(f"主题: {email_info['subject'][:50]}...")
                    print(f"发件人: {email_info['from'][:50]}...")
                    print(f"日期: {email_info['date']}")
                    print(f"正文长度: {len(email_info['body'])} 字符")
                    
                    # 保存测试结果
                    result_file = '/Users/lanlan/Downloads/python快递/test_result.json'
                    test_result = {
                        'provider': provider,
                        'server': server_config['server'],
                        'test_time': str(datetime.now()),
                        'email_count': len(email_ids),
                        'sample_email': {
                            'subject': email_info['subject'],
                            'from': email_info['from'],
                            'date': email_info['date'],
                            'body_length': len(email_info['body'])
                        }
                    }
                    
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(test_result, f, ensure_ascii=False, indent=2)
                    
                    print(f"\n测试结果已保存到: {result_file}")
                    print("\n✅ 所有测试通过！")
                    return True
            else:
                print("收件箱中没有邮件")
                return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {str(e)}")
        return False
    
    finally:
        client.disconnect()

def batch_test():
    """
    批量测试多个邮箱配置
    """
    print("=== 批量配置测试 ===")
    print("此功能需要在代码中预设多个测试账号")
    print("出于安全考虑，请手动修改此函数添加测试账号")
    
    # 示例批量测试结构
    test_accounts = [
        # {
        #     'provider': 'gmail',
        #     'username': 'your_gmail@gmail.com',
        #     'password': 'your_app_password'
        # },
        # {
        #     'provider': 'qq',
        #     'username': 'your_qq@qq.com',
        #     'password': 'your_authorization_code'
        # }
    ]
    
    if not test_accounts:
        print("请在代码中添加测试账号信息")
        return
    
    results = []
    for account in test_accounts:
        print(f"\n测试账号: {account['username']}")
        # 这里可以调用测试逻辑
        # result = test_single_account(account)
        # results.append(result)
    
    print(f"\n批量测试完成，共测试 {len(test_accounts)} 个账号")

def main():
    """
    主函数
    """
    print("IMAP邮箱测试工具")
    print("1. 快速测试")
    print("2. 批量测试")
    print("3. 退出")
    
    choice = input("\n请选择操作 (1-3): ").strip()
    
    if choice == '1':
        quick_test()
    elif choice == '2':
        batch_test()
    elif choice == '3':
        print("退出程序")
    else:
        print("无效选择")

if __name__ == "__main__":
    from datetime import datetime