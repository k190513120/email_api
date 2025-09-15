#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IMAP邮箱连接测试脚本
支持通过用户名和授权码连接邮箱服务器，获取和解析邮件内容
"""
import imaplib
import ssl
import json
from datetime import datetime

# 避免使用可能依赖cgi的email模块功能
try:
    import email
    from email.header import decode_header
except ImportError:
    # Python 3.13兼容性处理
    email = None
    decode_header = None

class IMAPEmailClient:
    """IMAP邮箱客户端类"""
    
    def __init__(self, server, port=993, use_ssl=True):
        """
        初始化IMAP客户端
        
        Args:
            server (str): IMAP服务器地址
            port (int): 端口号，默认993（SSL）
            use_ssl (bool): 是否使用SSL连接
        """
        self.server = server
        self.port = port
        self.use_ssl = use_ssl
        self.imap = None
        self.connected = False
    
    def connect(self, username, password):
        """
        连接到IMAP服务器并登录
        
        Args:
            username (str): 邮箱用户名
            password (str): 邮箱密码或授权码
            
        Returns:
            bool: 连接是否成功
        """
        try:
            print(f"正在连接到 {self.server}:{self.port}...")
            
            if self.use_ssl:
                # 创建SSL上下文
                context = ssl.create_default_context()
                self.imap = imaplib.IMAP4_SSL(self.server, self.port, ssl_context=context)
            else:
                self.imap = imaplib.IMAP4(self.server, self.port)
            
            print("正在登录...")
            result = self.imap.login(username, password)
            
            if result[0] == 'OK':
                self.connected = True
                print("登录成功！")
                return True
            else:
                print(f"登录失败: {result[1]}")
                return False
                
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False
    
    def list_folders(self):
        """
        列出所有邮箱文件夹
        
        Returns:
            list: 文件夹列表
        """
        if not self.connected:
            print("请先连接到邮箱服务器")
            return []
        
        try:
            result, folders = self.imap.list()
            if result == 'OK':
                folder_list = []
                for folder in folders:
                    # 解析文件夹信息
                    folder_info = folder.decode('utf-8')
                    folder_list.append(folder_info)
                return folder_list
        except Exception as e:
            print(f"获取文件夹列表失败: {str(e)}")
            return []
    
    def select_folder(self, folder='INBOX'):
        """
        选择邮箱文件夹
        
        Args:
            folder (str): 文件夹名称，默认为收件箱
            
        Returns:
            bool: 选择是否成功
        """
        if not self.connected:
            print("请先连接到邮箱服务器")
            return False
        
        try:
            result, data = self.imap.select(folder)
            if result == 'OK':
                email_count = int(data[0])
                print(f"已选择文件夹 '{folder}'，共有 {email_count} 封邮件")
                return True
            else:
                print(f"选择文件夹失败: {data}")
                return False
        except Exception as e:
            print(f"选择文件夹失败: {str(e)}")
            return False
    
    def search_emails(self, criteria='ALL', limit=10):
        """
        搜索邮件
        
        Args:
            criteria (str): 搜索条件，默认为'ALL'
            limit (int): 限制返回的邮件数量
            
        Returns:
            list: 邮件ID列表
        """
        if not self.connected:
            print("请先连接到邮箱服务器")
            return []
        
        try:
            result, data = self.imap.search(None, criteria)
            if result == 'OK':
                email_ids = data[0].split()
                # 限制返回数量，获取最新的邮件
                if limit and len(email_ids) > limit:
                    email_ids = email_ids[-limit:]
                return [email_id.decode() for email_id in email_ids]
            else:
                print(f"搜索邮件失败: {data}")
                return []
        except Exception as e:
            print(f"搜索邮件失败: {str(e)}")
            return []
    
    def decode_mime_words(self, s):
        """
        解码MIME编码的字符串
        
        Args:
            s (str): 待解码的字符串
            
        Returns:
            str: 解码后的字符串
        """
        # 检查decode_header是否可用
        if decode_header is None:
            # 简单返回原字符串
            return str(s) if s else ''
            
        try:
            decoded_fragments = decode_header(s)
            decoded_string = ''
            
            for fragment, encoding in decoded_fragments:
                if isinstance(fragment, bytes):
                    if encoding:
                        try:
                            decoded_string += fragment.decode(encoding)
                        except (UnicodeDecodeError, LookupError):
                            decoded_string += fragment.decode('utf-8', errors='ignore')
                    else:
                        decoded_string += fragment.decode('utf-8', errors='ignore')
                else:
                    decoded_string += fragment
            
            return decoded_string
        except Exception:
            # 如果解码失败，返回原字符串
            return str(s) if s else ''
    
    def get_email_content(self, email_id):
        """
        获取邮件内容
        
        Args:
            email_id (str): 邮件ID
            
        Returns:
            dict: 邮件信息字典
        """
        if not self.connected:
            print("请先连接到邮箱服务器")
            return None
        
        try:
            result, data = self.imap.fetch(email_id, '(RFC822)')
            if result == 'OK':
                raw_email = data[0][1]
                
                # 检查email模块是否可用
                if email is None:
                    print("email模块不可用，无法解析邮件内容")
                    return None
                    
                email_message = email.message_from_bytes(raw_email)
                
                # 解析邮件头信息
                subject = self.decode_mime_words(email_message.get('Subject', ''))
                from_addr = self.decode_mime_words(email_message.get('From', ''))
                to_addr = self.decode_mime_words(email_message.get('To', ''))
                date = email_message.get('Date', '')
                
                # 解析邮件正文
                body = self.extract_email_body(email_message)
                
                # 解析邮件附件
                attachments = self.extract_email_attachments(email_message)
                
                email_info = {
                    'id': email_id,
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'date': date,
                    'body': body,
                    'attachments': attachments
                }
                
                return email_info
            else:
                print(f"获取邮件失败: {data}")
                return None
        except Exception as e:
            print(f"获取邮件内容失败: {str(e)}")
            return None
    
    def extract_email_body(self, email_message):
        """
        提取邮件正文内容
        
        Args:
            email_message: 邮件消息对象
            
        Returns:
            str: 邮件正文
        """
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # 跳过附件
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
                elif content_type == "text/html" and not body:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body
    
    def extract_email_attachments(self, email_message):
        """
        提取邮件附件信息
        
        Args:
            email_message: 邮件消息对象
            
        Returns:
            list: 附件信息列表，每个附件包含filename、size、content等信息
        """
        attachments = []
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # 检查是否为附件
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        # 解码文件名
                        filename = self.decode_mime_words(filename)
                        
                        # 获取附件内容
                        try:
                            content = part.get_payload(decode=True)
                            if content:
                                attachment_info = {
                                    'filename': filename,
                                    'size': len(content),
                                    'content_type': part.get_content_type(),
                                    'content': content  # 二进制内容
                                }
                                attachments.append(attachment_info)
                        except Exception as e:
                            print(f"提取附件 {filename} 失败: {str(e)}")
                            continue
        
        return attachments
    
    def disconnect(self):
        """
        断开IMAP连接
        """
        if self.connected and self.imap:
            try:
                self.imap.close()
                self.imap.logout()
                self.connected = False
                print("已断开连接")
            except:
                pass

# 常用邮箱服务器配置
EMAIL_SERVERS = {
    'gmail': {
        'server': 'imap.gmail.com',
        'port': 993,
        'ssl': True
    },
    'outlook': {
        'server': 'outlook.office365.com',
        'port': 993,
        'ssl': True
    },
    'yahoo': {
        'server': 'imap.mail.yahoo.com',
        'port': 993,
        'ssl': True
    },
    'qq': {
        'server': 'imap.qq.com',
        'port': 993,
        'ssl': True
    },
    '163': {
        'server': 'imap.163.com',
        'port': 993,
        'ssl': True
    },
    '126': {
        'server': 'imap.126.com',
        'port': 993,
        'ssl': True
    }
}

def main():
    """
    主函数 - 测试IMAP邮箱连接
    """
    print("=== IMAP邮箱连接测试 ===")
    print("支持的邮箱服务商:")
    for provider in EMAIL_SERVERS.keys():
        print(f"  - {provider}")
    print()
    
    # 用户输入配置
    provider = input("请选择邮箱服务商 (或输入'custom'自定义): ").lower().strip()
    
    if provider == 'custom':
        server = input("请输入IMAP服务器地址: ").strip()
        port = int(input("请输入端口号 (默认993): ") or "993")
        use_ssl = input("是否使用SSL (y/n, 默认y): ").lower().strip() != 'n'
    elif provider in EMAIL_SERVERS:
        config = EMAIL_SERVERS[provider]
        server = config['server']
        port = config['port']
        use_ssl = config['ssl']
        print(f"使用 {provider} 配置: {server}:{port}")
    else:
        print("不支持的邮箱服务商")
        return
    
    username = input("请输入邮箱用户名: ").strip()
    password = input("请输入邮箱密码或授权码: ").strip()
    
    if not username or not password:
        print("用户名和密码不能为空")
        return
    
    # 创建IMAP客户端并连接
    client = IMAPEmailClient(server, port, use_ssl)
    
    if not client.connect(username, password):
        return
    
    try:
        # 列出文件夹
        print("\n=== 邮箱文件夹 ===")
        folders = client.list_folders()
        for folder in folders[:5]:  # 只显示前5个
            print(folder)
        
        # 选择收件箱
        if client.select_folder('INBOX'):
            # 搜索最新的5封邮件
            print("\n=== 获取最新邮件 ===")
            email_ids = client.search_emails('ALL', limit=5)
            
            if email_ids:
                print(f"找到 {len(email_ids)} 封邮件")
                
                # 获取第一封邮件的详细信息
                if email_ids:
                    print("\n=== 第一封邮件详情 ===")
                    email_info = client.get_email_content(email_ids[0])
                    
                    if email_info:
                        print(f"主题: {email_info['subject']}")
                        print(f"发件人: {email_info['from']}")
                        print(f"收件人: {email_info['to']}")
                        print(f"日期: {email_info['date']}")
                        print(f"正文预览: {email_info['body'][:200]}...")
                        
                        # 保存邮件信息到文件
                        with open('/Users/lanlan/Downloads/python快递/email_sample.json', 'w', encoding='utf-8') as f:
                            json.dump(email_info, f, ensure_ascii=False, indent=2)
                        print("\n邮件详情已保存到 email_sample.json")
            else:
                print("未找到邮件")
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n操作过程中出现错误: {str(e)}")
    finally:
        # 断开连接
        client.disconnect()

if __name__ == "__main__":
    main()