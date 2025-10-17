#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub Actions 邮件同步到飞书多维表格脚本
支持从环境变量读取配置，实现邮件获取和数据同步
使用BaseOpenSDK进行飞书多维表格操作
支持多种邮箱类型：飞书邮箱、Gmail、QQ邮箱、网易邮箱等
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from email_providers import EmailProviderFactory

from baseopensdk import BaseClient
from baseopensdk.api.base.v1 import *
from baseopensdk.api.drive.v1 import *

class EmailSyncAction:
    def __init__(self, config=None):
        """初始化邮件同步操作类"""
        if config:
            self.config = self.validate_config(config)
        else:
            self.config = self.load_config_from_env()
        self.sync_results = []
        self.sync_logs = []
        self.feishu_client = None
        
    def load_config_from_env(self):
        """从环境变量加载配置"""
        config = {
            'bitable_url': os.getenv('BITABLE_URL'),
            'personal_base_token': os.getenv('PERSONAL_BASE_TOKEN'),
            'email_username': os.getenv('EMAIL_USERNAME'),
            'email_password': os.getenv('EMAIL_PASSWORD'),
            'email_provider': os.getenv('EMAIL_PROVIDER', 'feishu'),
            'email_count': int(os.getenv('EMAIL_COUNT', '50'))  # 修改默认值为50
        }
        
        # 从BITABLE_URL中解析app_token
        if config['bitable_url']:
            try:
                bitable_info = self.parse_bitable_url(config['bitable_url'])
                config['app_token'] = bitable_info['app_token']
            except Exception as e:
                raise ValueError(f"解析BITABLE_URL失败: {str(e)}")
        
        # 验证必需的配置
        required_fields = ['bitable_url', 'personal_base_token', 
                          'email_username', 'email_password']
        
        missing_fields = [field for field in required_fields if not config[field]]
        if missing_fields:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_fields)}")
            
        return config
    
    def validate_config(self, config):
        """验证传入的配置参数"""
        # 从BITABLE_URL中解析app_token
        if config.get('bitable_url'):
            try:
                bitable_info = self.parse_bitable_url(config['bitable_url'])
                config['app_token'] = bitable_info['app_token']
            except Exception as e:
                raise ValueError(f"解析BITABLE_URL失败: {str(e)}")
        
        # 设置默认值
        config.setdefault('email_provider', 'feishu')
        config.setdefault('email_count', 50)  # 修改默认值为50
        
        # 验证必需的配置
        required_fields = ['bitable_url', 'personal_base_token', 
                          'email_username', 'email_password']
        
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
    
    def init_feishu_client(self):
        """初始化飞书BaseOpenSDK客户端"""
        try:
            self.log_message('INFO', "初始化飞书BaseOpenSDK客户端")
            
            self.feishu_client = BaseClient.builder() \
                .app_token(self.config['app_token']) \
                .personal_base_token(self.config['personal_base_token']) \
                .build()
                
            self.log_message('INFO', "飞书客户端初始化成功")
            
        except Exception as e:
            self.log_message('ERROR', "飞书客户端初始化失败", str(e))
            raise
    
    def upload_attachment_to_drive(self, attachment):
        """
        将附件上传到飞书Drive并获取file_token
        
        Args:
            attachment (dict): 附件信息，包含filename、content、size等
            
        Returns:
            str: file_token，如果上传失败返回None
        """
        try:
            filename = attachment.get('filename', 'unknown_file')
            content = attachment.get('content')
            size = attachment.get('size', 0)
            
            if not content:
                self.log_message('WARNING', f"附件 {filename} 内容为空，跳过上传")
                return None
            
            self.log_message('INFO', f"开始上传附件: {filename} ({size} bytes)")
            
            # 构建上传请求
            request = UploadAllMediaRequest.builder() \
                .request_body(UploadAllMediaRequestBody.builder()
                    .file_name(filename)
                    .parent_type("bitable_image")
                    .parent_node(self.config['app_token'])
                    .size(size)
                    .file(content)
                    .build()) \
                .build()
            
            # 上传文件
            response = self.feishu_client.drive.v1.media.upload_all(request)
            
            if response.code == 0 and response.data and response.data.file_token:
                file_token = response.data.file_token
                self.log_message('INFO', f"附件 {filename} 上传成功，file_token: {file_token}")
                return file_token
            else:
                error_msg = f"上传附件失败: {response.msg if response.msg else '未知错误'}"
                self.log_message('ERROR', f"附件 {filename} 上传失败", error_msg)
                return None
                
        except Exception as e:
            self.log_message('ERROR', f"上传附件 {attachment.get('filename', 'unknown')} 时出错", str(e))
            return None
    
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
            
            # 获取邮件
            emails = email_provider.get_emails(count=self.config['email_count'])
            
            if not emails:
                self.log_message('WARNING', "未获取到任何邮件")
                return []
            
            # 打印邮件数据结构供用户查看
            for i, email_info in enumerate(emails):
                print(f"\n=== 邮件 {i+1} 的完整数据结构 ===")
                print(f"邮件ID: {email_info.get('id', 'N/A')}")
                print(f"主题: {email_info.get('subject', 'N/A')}")
                print(f"发件人: {email_info.get('sender', 'N/A')}")
                print(f"收件人: {email_info.get('recipient', 'N/A')}")
                print(f"日期: {email_info.get('date', 'N/A')}")
                print(f"正文长度: {len(email_info.get('body', '')) if email_info.get('body') else 0} 字符")
                print(f"正文内容(前200字符): {(email_info.get('body', '') or '')[:200]}...")
                print(f"是否有附件: {email_info.get('has_attachments', False)}")
                print("=" * 50)
            
            # 关闭连接
            email_provider.close_connections()
            
            return emails
            
        except Exception as e:
            self.log_message('ERROR', "获取邮件失败", str(e))
            raise
    
    def sync_to_feishu_bitable(self, emails):
        """使用BaseOpenSDK同步邮件到飞书多维表格"""
        try:
            self.log_message('INFO', "开始同步邮件到飞书多维表格")
            
            # 初始化飞书客户端
            if not self.feishu_client:
                self.init_feishu_client()
            
            # 解析多维表格URL获取app_token和table_id
            bitable_info = self.parse_bitable_url(self.config['bitable_url'])
            app_token = bitable_info['app_token']
            table_id = bitable_info['table_id']
            
            # 转换邮件数据为多维表格记录格式
            records = []
            for email in emails:
                # 转换日期格式为时间戳
                date_timestamp = None
                if email.get('date'):
                    try:
                        # 使用更兼容的日期解析方式
                        import time
                        from datetime import datetime
                        
                        date_str = email.get('date')
                        # 尝试多种日期格式解析
                        try:
                            # 标准RFC2822格式
                            parsed_date = datetime.strptime(date_str.split(' (')[0], '%a, %d %b %Y %H:%M:%S %z')
                        except:
                            try:
                                # 简化格式
                                parsed_date = datetime.strptime(date_str[:25], '%a, %d %b %Y %H:%M:%S')
                            except:
                                # 使用当前时间作为fallback
                                parsed_date = datetime.now()
                        
                        # 转换为毫秒时间戳
                        date_timestamp = int(parsed_date.timestamp() * 1000)
                    except Exception as e:
                        self.log_message('WARNING', f"日期解析失败: {email.get('date')}, 错误: {str(e)}")
                        # 使用当前时间戳作为fallback
                        date_timestamp = int(datetime.now().timestamp() * 1000)
                
                # 分别映射到对应字段
                record = {
                    "fields": {
                        "邮件ID": email.get('id', ''),  # 邮件ID字段
                        "主题": email.get('subject', '')[:500],  # 主题字段
                        "发件人": email.get('sender', '')[:200],   # 发件人字段
                        "邮件内容": (email.get('body', '') or '')[:2000],  # 邮件内容字段
                    }
                }
                
                # 只有成功解析日期时才添加日期字段
                if date_timestamp:
                    record["fields"]["日期"] = date_timestamp
                
                # 处理附件信息（新的邮件提供商架构中，附件信息通过has_attachments字段提供）
                if email.get('has_attachments', False):
                    # 在邮件内容中添加附件标识
                    current_content = record["fields"]["邮件内容"]
                    attachment_text = "\n\n[此邮件包含附件]"
                    record["fields"]["邮件内容"] = (current_content + attachment_text)[:2000]
                
                records.append(record)
            
            self.log_message('INFO', f"准备同步 {len(records)} 条记录")
            
            # 查询现有记录，检查日期是否已存在
            existing_dates = self.get_existing_email_dates(app_token, table_id)
            
            # 过滤掉已存在的邮件
            new_records = []
            skipped_count = 0
            
            for record in records:
                date_timestamp = record["fields"].get("日期")
                if date_timestamp and date_timestamp in existing_dates:
                    skipped_count += 1
                    email_subject = record["fields"].get("主题", "未知主题")[:50]
                    self.log_message('INFO', f"跳过重复邮件: {email_subject} (日期: {date_timestamp})")
                else:
                    new_records.append(record)
            
            self.log_message('INFO', f"跳过重复邮件 {skipped_count} 条，准备同步新邮件 {len(new_records)} 条")
            
            if not new_records:
                self.log_message('INFO', "没有新邮件需要同步")
                return {
                    'success': True,
                    'message': f'没有新邮件需要同步，跳过重复邮件 {skipped_count} 条',
                    'synced_count': 0,
                    'skipped_count': skipped_count
                }
            
            # 批量创建记录
            request = BatchCreateAppTableRecordRequest.builder() \
                .table_id(table_id) \
                .request_body(
                    BatchCreateAppTableRecordRequestBody.builder() \
                        .records(new_records) \
                        .build()
                ) \
                .build()
            
            response = self.feishu_client.base.v1.app_table_record.batch_create(request)
            
            if response.code == 0:
                synced_count = len(getattr(response.data, 'records', []))
                message = f'成功同步 {synced_count} 条记录'
                if skipped_count > 0:
                    message += f'，跳过重复邮件 {skipped_count} 条'
                self.log_message('INFO', f"同步成功: {message}")
                return {
                    'success': True,
                    'message': message,
                    'synced_count': synced_count,
                    'skipped_count': skipped_count
                }
            else:
                error_msg = f"飞书API返回错误: {response.msg}"
                self.log_message('ERROR', "飞书同步失败", error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.log_message('ERROR', "同步到飞书多维表格失败", str(e))
            raise
    
    def get_existing_email_dates(self, app_token, table_id):
        """查询现有记录中的日期字段"""
        try:
            # 使用ListAppTableRecordRequest来查询现有记录
            
            self.log_message('INFO', "查询现有邮件日期")
            
            existing_dates = set()
            page_token = None
            
            while True:
                # 构建查询请求
                request = ListAppTableRecordRequest.builder() \
                    .table_id(table_id) \
                    .page_size(500) \
                    .build()
                
                if page_token:
                    request.page_token = page_token
                
                response = self.feishu_client.base.v1.app_table_record.list(request)
                
                if response.code != 0:
                    self.log_message('WARNING', f"查询现有记录失败: {response.msg}")
                    break
                
                # 提取日期字段
                if hasattr(response.data, 'items') and response.data.items:
                    for item in response.data.items:
                        if hasattr(item, 'fields') and item.fields:
                            date_timestamp = item.fields.get('日期')
                            if date_timestamp:
                                existing_dates.add(date_timestamp)
                
                # 检查是否还有更多页
                if not hasattr(response.data, 'has_more') or not response.data.has_more:
                    break
                
                page_token = getattr(response.data, 'page_token', None)
                if not page_token:
                    break
            
            self.log_message('INFO', f"找到 {len(existing_dates)} 个现有邮件日期")
            return existing_dates
            
        except Exception as e:
            self.log_message('WARNING', f"查询现有邮件日期失败: {str(e)}")
            return set()  # 查询失败时返回空集合，允许所有邮件同步
    
    def parse_bitable_url(self, url):
        """解析飞书多维表格URL"""
        try:
            # 示例URL: https://example.feishu.cn/base/bascnxxx?table=tblxxx
            import re
            
            # 提取app_token (base后面的部分)
            app_token_match = re.search(r'/base/([^/?]+)', url)
            if not app_token_match:
                raise ValueError("无法从URL中提取app_token")
            app_token = app_token_match.group(1)
            
            # 提取table_id (table参数)
            table_id_match = re.search(r'[?&]table=([^&]+)', url)
            if not table_id_match:
                raise ValueError("无法从URL中提取table_id")
            table_id = table_id_match.group(1)
            
            return {
                'app_token': app_token,
                'table_id': table_id
            }
        except Exception as e:
            raise ValueError(f"解析多维表格URL失败: {str(e)}")
    

    
    def save_results(self):
        """保存同步结果到文件"""
        try:
            # 清理邮件数据，移除不可序列化的bytes内容
            cleaned_results = []
            for email in self.sync_results:
                cleaned_email = email.copy()
                # 移除附件的二进制内容，只保留元数据
                if 'attachments' in cleaned_email:
                    cleaned_attachments = []
                    for att in cleaned_email['attachments']:
                        if isinstance(att, dict):
                            cleaned_att = {k: v for k, v in att.items() if k != 'content'}
                            cleaned_attachments.append(cleaned_att)
                        else:
                            cleaned_attachments.append(att)
                    cleaned_email['attachments'] = cleaned_attachments
                cleaned_results.append(cleaned_email)
            
            # 保存同步结果
            with open('sync_result.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'config': {
                        'email_provider': self.config['email_provider'],
                        'email_username': self.config['email_username'],
                        'email_count': self.config['email_count']
                    },
                    'results': cleaned_results
                }, f, ensure_ascii=False, indent=2)
            
            # 保存日志
            with open('sync_logs.json', 'w', encoding='utf-8') as f:
                json.dump(self.sync_logs, f, ensure_ascii=False, indent=2)
                
            self.log_message('INFO', "结果文件保存成功")
            
        except Exception as e:
            self.log_message('ERROR', "保存结果文件失败", str(e))
    
    def run_sync(self):
        """执行邮件同步并返回结果（用于HTTP API调用）"""
        try:
            self.log_message('INFO', "开始邮件同步任务")
            
            # 1. 获取邮件
            emails = self.get_emails_from_imap()
            
            if not emails:
                result = {
                    'success': True,
                    'message': '没有找到邮件',
                    'synced_count': 0
                }
            else:
                # 2. 同步到飞书多维表格
                result = self.sync_to_feishu_bitable(emails)
                
            self.sync_results = emails
            
            # 3. 保存结果
            self.save_results()
            
            self.log_message('INFO', "邮件同步任务完成")
            return result
            
        except Exception as e:
            error_msg = f"邮件同步任务失败: {str(e)}"
            self.log_message('ERROR', error_msg, traceback.format_exc())
            
            # 保存错误结果
            try:
                self.save_results()
            except:
                pass
            
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }
    
    def run(self):
        """执行完整的邮件同步流程"""
        try:
            result = self.run_sync()
            if not result['success']:
                sys.exit(1)
            
        except Exception as e:
            self.log_message('ERROR', "邮件同步任务失败", traceback.format_exc())
            sys.exit(1)

def main():
    """主函数"""
    print("=== GitHub Actions 邮件同步到飞书多维表格 (BaseOpenSDK) ===")
    
    try:
        sync_action = EmailSyncAction()
        sync_action.run()
        print("\n同步任务执行成功!")
        
    except Exception as e:
        print(f"\n同步任务执行失败: {str(e)}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()