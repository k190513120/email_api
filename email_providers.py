#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""邮箱提供商基类和具体实现
支持多种邮箱类型：飞书邮箱、Gmail、QQ邮箱、网易邮箱等
"""

import imaplib
import smtplib
import email
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
import ssl
import logging

logger = logging.getLogger(__name__)

class EmailProvider(ABC):
    """邮箱提供商基类"""
    
    def __init__(self, username: str, password: str, **kwargs):
        self.username = username
        self.password = password
        self.config = kwargs
        self.imap_client = None
        self.smtp_client = None
    
    @abstractmethod
    def get_imap_config(self) -> Dict[str, Any]:
        """获取IMAP配置"""
        pass
    
    @abstractmethod
    def get_smtp_config(self) -> Dict[str, Any]:
        """获取SMTP配置"""
        pass
    
    def connect_imap(self) -> bool:
        """连接IMAP服务器"""
        try:
            imap_config = self.get_imap_config()
            self.imap_client = imaplib.IMAP4_SSL(
                imap_config['server'], 
                imap_config['port']
            )
            self.imap_client.login(self.username, self.password)
            logger.info(f"IMAP连接成功: {imap_config['server']}")
            return True
        except Exception as e:
            logger.error(f"IMAP连接失败: {str(e)}")
            return False
    
    def connect_smtp(self) -> bool:
        """连接SMTP服务器"""
        try:
            smtp_config = self.get_smtp_config()
            self.smtp_client = smtplib.SMTP_SSL(
                smtp_config['server'], 
                smtp_config['port']
            )
            self.smtp_client.login(self.username, self.password)
            logger.info(f"SMTP连接成功: {smtp_config['server']}")
            return True
        except Exception as e:
            logger.error(f"SMTP连接失败: {str(e)}")
            return False
    
    def get_emails(self, folder: str = 'INBOX', count: int = 50) -> List[Dict[str, Any]]:
        """获取邮件列表"""
        if not self.imap_client:
            if not self.connect_imap():
                return []
        
        try:
            self.imap_client.select(folder)
            _, message_ids = self.imap_client.search(None, 'ALL')
            
            if not message_ids[0]:
                return []
            
            # 获取最新的邮件
            ids = message_ids[0].split()
            latest_ids = ids[-count:] if len(ids) > count else ids
            
            emails = []
            for msg_id in reversed(latest_ids):  # 最新的邮件在前
                try:
                    _, msg_data = self.imap_client.fetch(msg_id, '(RFC822)')
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # 解析邮件信息
                    email_info = self._parse_email(email_message)
                    email_info['id'] = msg_id.decode()
                    emails.append(email_info)
                    
                except Exception as e:
                    logger.error(f"解析邮件失败 (ID: {msg_id}): {str(e)}")
                    continue
            
            return emails
            
        except Exception as e:
            logger.error(f"获取邮件失败: {str(e)}")
            return []
    
    def _parse_email(self, email_message) -> Dict[str, Any]:
        """解析邮件内容"""
        def decode_mime_words(s):
            """解码MIME编码的字符串"""
            if not s:
                return ""
            decoded_fragments = decode_header(s)
            decoded_string = ""
            for fragment, encoding in decoded_fragments:
                if isinstance(fragment, bytes):
                    if encoding:
                        decoded_string += fragment.decode(encoding)
                    else:
                        decoded_string += fragment.decode('utf-8', errors='ignore')
                else:
                    decoded_string += fragment
            return decoded_string
        
        # 基本信息
        subject = decode_mime_words(email_message.get('Subject', ''))
        sender = decode_mime_words(email_message.get('From', ''))
        recipient = decode_mime_words(email_message.get('To', ''))
        date = email_message.get('Date', '')
        
        # 获取邮件正文
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        # 提取附件详细信息
        attachments = []
        try:
            for part in email_message.walk():
                filename = part.get_filename()
                if filename:
                    # 解码文件名
                    decoded_filename = decode_mime_words(filename)
                    
                    # 获取附件二进制内容
                    content = part.get_payload(decode=True)
                    if not content:
                        continue
                        
                    file_size = len(content)
                    
                    # 检查文件大小限制（飞书限制2GB）
                    max_size = 1024 * 1024 * 1024 * 2  # 2GB
                    if file_size > max_size:
                        logger.warning(f"附件 {decoded_filename} 大小 {file_size} 超过限制 {max_size}，跳过")
                        continue
                    
                    # 检查文件名长度限制（飞书限制250字符）
                    if len(decoded_filename) > 250:
                        logger.warning(f"附件文件名 {decoded_filename} 长度超过250字符，截断")
                        decoded_filename = decoded_filename[:247] + "..."
                    
                    # 获取MIME类型
                    content_type = part.get_content_type()
                    
                    # 将二进制内容转换为base64编码以便传输
                    import base64
                    content_base64 = base64.b64encode(content).decode('utf-8')
                    
                    attachment_info = {
                        'filename': decoded_filename,
                        'size': file_size,
                        'content_type': content_type,
                        'content': content_base64  # 添加base64编码的文件内容
                    }
                    attachments.append(attachment_info)
        except Exception as e:
            logger.error(f"解析附件信息失败: {str(e)}")
            # 如果解析失败，保持空列表，不影响整体功能
            attachments = []
        
        return {
            'subject': subject,
            'sender': sender,
            'recipient': recipient,
            'date': date,
            'body': body[:1000] if body else "",  # 限制正文长度
            'attachments': attachments,  # 改为附件详细信息数组
            'has_attachments': len(attachments) > 0  # 保持向后兼容性
        }
    
    def connect(self) -> bool:
        """连接到邮箱服务器（IMAP）"""
        return self.connect_imap()
    
    def disconnect(self):
        """断开连接"""
        self.close_connections()
    
    def close_connections(self):
        """关闭连接"""
        if self.imap_client:
            try:
                self.imap_client.close()
                self.imap_client.logout()
            except:
                pass
        
        if self.smtp_client:
            try:
                self.smtp_client.quit()
            except:
                pass


class LarkEmailProvider(EmailProvider):
    """飞书邮箱提供商"""
    
    def get_imap_config(self) -> Dict[str, Any]:
        return {
            'server': 'imap.feishu.cn',
            'port': 993
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        return {
            'server': 'smtp.feishu.cn',
            'port': 465
        }


class GmailProvider(EmailProvider):
    """Gmail邮箱提供商"""
    
    def get_imap_config(self) -> Dict[str, Any]:
        return {
            'server': 'imap.gmail.com',
            'port': 993
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        return {
            'server': 'smtp.gmail.com',
            'port': 465
        }


class QQEmailProvider(EmailProvider):
    """QQ邮箱提供商"""
    
    def get_imap_config(self) -> Dict[str, Any]:
        return {
            'server': 'imap.qq.com',
            'port': 993
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        return {
            'server': 'smtp.qq.com',
            'port': 465
        }


class NetEaseEmailProvider(EmailProvider):
    """网易邮箱提供商（163邮箱）"""
    
    def get_imap_config(self) -> Dict[str, Any]:
        return {
            'server': 'imap.163.com',
            'port': 993
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        return {
            'server': 'smtp.163.com',
            'port': 465
        }


class EmailProviderFactory:
    """邮箱提供商工厂类"""
    
    PROVIDERS = {
        'lark': LarkEmailProvider,
        'feishu': LarkEmailProvider,  # 别名
        'gmail': GmailProvider,
        'google': GmailProvider,  # 别名
        'qq': QQEmailProvider,
        'netease': NetEaseEmailProvider,
        '163': NetEaseEmailProvider,  # 别名
    }
    
    @classmethod
    def create_provider(cls, provider_type: str, username: str, password: str, **kwargs) -> EmailProvider:
        """创建邮箱提供商实例"""
        provider_type = provider_type.lower()
        
        if provider_type not in cls.PROVIDERS:
            raise ValueError(f"不支持的邮箱类型: {provider_type}. 支持的类型: {list(cls.PROVIDERS.keys())}")
        
        provider_class = cls.PROVIDERS[provider_type]
        return provider_class(username, password, **kwargs)
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的邮箱提供商列表"""
        return list(cls.PROVIDERS.keys())