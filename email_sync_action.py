#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""邮件获取脚本
支持从环境变量读取配置，实现邮件获取功能
支持多种邮箱类型：飞书邮箱、Gmail、QQ邮箱、网易邮箱等
注意：已移除飞书同步功能，仅保留邮件获取
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from email_providers import EmailProviderFactory

class EmailSyncAction:
    def __init__(self, config=None):
        """初始化邮件获取操作类"""
        if config:
            self.config = self.validate_config(config)
        else:
            self.config = self.load_config_from_env()
        self.sync_results = []
        self.sync_logs = []
        
    def load_config_from_env(self):
        """从环境变量加载配置"""
        config = {
            'email_username': os.getenv('EMAIL_USERNAME'),
            'email_password': os.getenv('EMAIL_PASSWORD'),
            'email_provider': os.getenv('EMAIL_PROVIDER', 'feishu'),
            'email_count': int(os.getenv('EMAIL_COUNT', '50'))
        }
        
        # 验证必需的配置（仅邮件相关）
        required_fields = ['email_username', 'email_password']
        
        missing_fields = [field for field in required_fields if not config[field]]
        if missing_fields:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_fields)}")
            
        return config
    
    def validate_config(self, config):
        """验证传入的配置参数"""
        # 设置默认值
        config.setdefault('email_provider', 'feishu')
        config.setdefault('email_count', 50)
        
        # 验证必需的配置（仅邮件相关）
        required_fields = ['email_username', 'email_password']
        
        missing_fields = [field for field in required_fields if not config.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必需的配置参数: {', '.join(missing_fields)}")
            
        return config
    
    def log_message(self, level, message, details=None):
        """记录日志消息"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        if details:
            log_entry['details'] = details
            
        self.sync_logs.append(log_entry)
        print(f"[{level}] {message}")
        if details:
            print(f"详情: {details}")
    
    def get_emails_from_imap(self):
        """从IMAP服务器获取邮件"""
        try:
            self.log_message('INFO', f"开始连接 {self.config['email_provider']} 邮箱服务器")
            
            # 创建邮箱提供商实例
            email_provider = EmailProviderFactory.create_provider(
                self.config['email_provider'],
                self.config['email_username'],
                self.config['email_password']
            )
            
            # 连接到邮箱服务器
            email_provider.connect()
            self.log_message('INFO', "邮箱服务器连接成功")
            
            # 获取邮件
            emails = email_provider.get_emails(count=self.config['email_count'])
            self.log_message('INFO', f"成功获取 {len(emails)} 封邮件")
            
            # 断开连接
            email_provider.disconnect()
            
            return emails
            
        except Exception as e:
            self.log_message('ERROR', "获取邮件失败", str(e))
            raise
    
    def sync_emails(self, emails=None):
        """
        邮件获取主函数（已移除飞书同步功能）
        
        Args:
            emails: 可选的邮件列表，如果不提供则从IMAP获取
            
        Returns:
            dict: 包含获取结果的字典
        """
        try:
            self.log_message('INFO', "开始邮件获取操作")
            
            # 如果没有提供邮件列表，则从IMAP获取
            if emails is None:
                emails = self.get_emails_from_imap()
            
            # 处理邮件数据
            processed_emails = []
            for email in emails:
                try:
                    processed_email = {
                        'subject': email.get('subject', ''),
                        'sender': email.get('sender', ''),
                        'date': email.get('date', ''),
                        'body': email.get('body', ''),
                        'has_attachments': email.get('has_attachments', False),
                        'attachments': email.get('attachments', [])  # 添加附件详细信息
                    }
                    processed_emails.append(processed_email)
                    
                except Exception as e:
                    self.log_message('WARNING', f"处理邮件时出错: {str(e)}")
                    continue
            
            # 记录结果
            result = {
                'success': True,
                'total_emails': len(processed_emails),
                'emails': processed_emails,
                'logs': self.sync_logs
            }
            
            self.log_message('INFO', f"邮件获取完成，共处理 {len(processed_emails)} 封邮件")
            return result
            
        except Exception as e:
            error_msg = f"邮件获取失败: {str(e)}"
            self.log_message('ERROR', error_msg)
            return {
                'success': False,
                'error': error_msg,
                'logs': self.sync_logs
            }

def main():
    """主函数"""
    try:
        print("=== 邮件获取脚本 ===")
        
        # 创建邮件同步实例
        email_sync = EmailSyncAction()
        
        # 执行邮件获取
        result = email_sync.sync_emails()
        
        # 输出结果
        if result['success']:
            print(f"\n✅ 邮件获取成功！")
            print(f"📧 获取邮件数量: {result['total_emails']}")
        else:
            print(f"\n❌ 邮件获取失败: {result['error']}")
            return 1
            
    except Exception as e:
        print(f"\n💥 程序执行出错: {str(e)}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())