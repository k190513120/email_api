#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTTP API服务器 - 邮件同步到飞书多维表格
提供HTTP接口来触发邮件同步功能
"""

import os
import json
import traceback
from datetime import datetime
from flask import Flask, request, jsonify
from email_sync_action import EmailSyncAction

app = Flask(__name__)

# 配置日志
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailSyncAPI:
    """邮件同步API类"""
    
    def __init__(self):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        self.app.add_url_rule('/', 'index', self.index, methods=['GET'])
        self.app.add_url_rule('/sync', 'sync_emails', self.sync_emails, methods=['POST'])
        self.app.add_url_rule('/health', 'health_check', self.health_check, methods=['GET'])
    
    def index(self):
        """首页"""
        return jsonify({
            'service': '邮件同步到飞书多维表格 API',
            'version': '1.0.0',
            'endpoints': {
                'POST /sync': '触发邮件同步',
                'GET /health': '健康检查',
                'GET /': '服务信息'
            },
            'timestamp': datetime.now().isoformat()
        })
    
    def health_check(self):
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        })
    
    def sync_emails(self):
        """邮件同步接口"""
        try:
            # 获取请求数据
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': '请求体不能为空，需要JSON格式数据'
                }), 400
            
            # 验证必需参数
            required_params = [
                'bitable_url',
                'personal_base_token', 
                'email_username',
                'email_password'
            ]
            
            missing_params = [param for param in required_params if not data.get(param)]
            if missing_params:
                return jsonify({
                    'success': False,
                    'error': f'缺少必需参数: {", ".join(missing_params)}'
                }), 400
            
            # 设置环境变量
            os.environ['BITABLE_URL'] = data['bitable_url']
            os.environ['PERSONAL_BASE_TOKEN'] = data['personal_base_token']
            os.environ['EMAIL_USERNAME'] = data['email_username']
            os.environ['EMAIL_PASSWORD'] = data['email_password']
            os.environ['EMAIL_PROVIDER'] = data.get('email_provider', 'feishu')
            os.environ['EMAIL_COUNT'] = str(data.get('email_count', 10))
            
            logger.info(f"开始邮件同步任务 - 用户: {data['email_username']}, 提供商: {data.get('email_provider', 'feishu')}")
            
            # 创建邮件同步实例并执行
            sync_action = EmailSyncAction()
            
            # 获取邮件
            emails = sync_action.get_emails_from_imap()
            
            if not emails:
                result = {
                    'success': True,
                    'message': '没有找到邮件',
                    'synced_count': 0,
                    'skipped_count': 0
                }
            else:
                # 同步到飞书多维表格
                result = sync_action.sync_to_feishu_bitable(emails)
            
            # 设置同步结果并保存
            sync_action.sync_results = emails
            sync_action.save_results()
            
            logger.info(f"邮件同步任务完成 - {result.get('message', '未知结果')}")
            
            # 返回结果
            response_data = {
                'success': True,
                'message': result.get('message', '同步完成'),
                'synced_count': result.get('synced_count', 0),
                'skipped_count': result.get('skipped_count', 0),
                'total_emails': len(emails),
                'timestamp': datetime.now().isoformat(),
                'logs': sync_action.sync_logs[-10:]  # 返回最后10条日志
            }
            
            return jsonify(response_data)
            
        except ValueError as e:
            # 配置错误
            error_msg = f"配置错误: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), 400
            
        except Exception as e:
            # 其他错误
            error_msg = f"同步失败: {str(e)}"
            error_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{error_trace}")
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动API服务器"""
        logger.info(f"启动邮件同步API服务器 - http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """主函数"""
    print("=== 邮件同步到飞书多维表格 HTTP API 服务器 ===")
    
    # 从环境变量获取配置
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '5000'))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'
    
    try:
        api = EmailSyncAPI()
        api.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(f"启动API服务器失败: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()