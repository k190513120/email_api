#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件模块兼容性处理
避免使用可能依赖cgi模块的email功能
"""

import imaplib
import ssl
import json
from datetime import datetime
import base64
import re

class EmailCompat:
    """邮件兼容性处理类"""
    
    @staticmethod
    def parse_email_from_bytes(raw_email):
        """从字节数据解析邮件，避免使用email.message_from_bytes"""
        try:
            # 将字节转换为字符串
            email_str = raw_email.decode('utf-8', errors='ignore')
            
            # 简单解析邮件头
            headers = {}
            body = ""
            
            lines = email_str.split('\n')
            in_headers = True
            
            for line in lines:
                if in_headers:
                    if line.strip() == "":
                        in_headers = False
                        continue
                    
                    # 解析头部
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip().lower()] = value.strip()
                else:
                    body += line + '\n'
            
            return {
                'subject': headers.get('subject', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'date': headers.get('date', ''),
                'body': body.strip()
            }
            
        except Exception as e:
            print(f"邮件解析失败: {e}")
            return {
                'subject': '解析失败',
                'from': '',
                'to': '',
                'date': '',
                'body': ''
            }
    
    @staticmethod
    def decode_mime_words(text):
        """简单的MIME解码，避免使用email.header.decode_header"""
        if not text:
            return ''
        
        try:
            # 处理基本的base64编码
            if '=?UTF-8?B?' in text:
                # 提取base64编码部分
                pattern = r'=\?UTF-8\?B\?([^?]+)\?='
                matches = re.findall(pattern, text)
                
                for match in matches:
                    try:
                        decoded = base64.b64decode(match).decode('utf-8')
                        text = text.replace(f'=?UTF-8?B?{match}?=', decoded)
                    except:
                        continue
            
            return text
        except:
            return str(text) if text else ''