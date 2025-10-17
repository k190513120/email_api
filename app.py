from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import traceback
from datetime import datetime
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入同步模块
try:
    import sys
    print(f"Python版本: {sys.version}")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.path[:3]}")
    
    # 测试基础依赖
    import requests
    print("✓ requests导入成功")
    
    from baseopensdk import BaseClient
    print("✓ BaseClient导入成功")
    
    from baseopensdk.api.base.v1 import *
    print("✓ baseopensdk.api.base.v1导入成功")
    
    from douyin_sync_action import DouyinVideoSync
    print("✓ DouyinVideoSync导入成功")
except ImportError as e:
    import traceback
    print(f"导入抖音同步模块错误: {e}")
    print(f"错误详情: {traceback.format_exc()}")
    DouyinVideoSync = None

# 导入邮件同步模块
try:
    from email_sync_action import EmailSyncAction
    print("✓ EmailSyncAction导入成功")
except ImportError as e:
    print(f"导入邮件同步模块错误: {e}")
    EmailSyncAction = None

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'lark-email-sync'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """首页"""
    return jsonify({
        'message': '飞书邮件同步服务',
        'version': '1.0.0',
        'endpoints': {
                'health': '/health',
                'sync_douyin': '/api/sync/douyin',
                'sync_email': '/api/sync/email',
                'status': '/api/status',
                'supported_providers': '/api/providers'
            }
    })

@app.route('/api/sync/douyin', methods=['POST'])
def sync_douyin_videos():
    """触发抖音视频同步"""
    try:
        if DouyinVideoSync is None:
            return jsonify({
                'success': False,
                'error': '抖音同步模块未正确加载',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # 获取请求参数
        data = request.get_json() or {}
        
        # 验证必需参数
        required_params = ['douyin_url', 'bitable_url', 'personal_base_token']
        missing_params = [param for param in required_params if not data.get(param)]
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f'缺少必需参数: {", ".join(missing_params)}',
                'timestamp': datetime.now().isoformat(),
                'message': '抖音视频同步失败'
            }), 400
        
        sync_count = data.get('sync_count', 15)
        
        logger.info(f"开始抖音视频同步，URL: {data['douyin_url']}, 数量: {sync_count}")
        
        # 创建同步器实例
        syncer = DouyinVideoSync(data['personal_base_token'])
        
        # 执行同步
        result = syncer.sync_videos_to_table(
            douyin_url=data['douyin_url'],
            bitable_url=data['bitable_url'],
            count=sync_count
        )
        
        logger.info(f"同步完成: {result}")
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat(),
            'message': '抖音视频同步完成'
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"同步失败: {error_msg}")
        logger.error(f"错误堆栈: {error_trace}")
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat(),
            'message': '抖音视频同步失败'
        }), 500

@app.route('/api/sync/email', methods=['POST'])
def sync_emails():
    """触发邮件同步"""
    try:
        if EmailSyncAction is None:
            return jsonify({
                'success': False,
                'error': '邮件同步模块未正确加载',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # 获取请求参数
        data = request.get_json() or {}
        
        # 验证必需参数
        required_params = ['personal_base_token', 'bitable_url', 'email_username', 'email_password']
        missing_params = [param for param in required_params if not data.get(param)]
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f'缺少必需参数: {", ".join(missing_params)}',
                'timestamp': datetime.now().isoformat(),
                'message': '邮件同步失败'
            }), 400
        
        # 验证邮箱类型
        email_provider = data.get('email_provider', 'feishu')
        from email_providers import EmailProviderFactory
        supported_providers = EmailProviderFactory.get_supported_providers()
        
        if email_provider not in supported_providers:
            return jsonify({
                'success': False,
                'error': f'不支持的邮箱类型: {email_provider}. 支持的类型: {supported_providers}',
                'timestamp': datetime.now().isoformat(),
                'message': '邮件同步失败'
            }), 400
        
        logger.info(f"开始邮件同步，目标表格: {data['bitable_url']}")
        
        # 创建同步器实例，传入完整配置
        config = {
            'personal_base_token': data['personal_base_token'],
            'bitable_url': data['bitable_url'],
            'email_username': data['email_username'],
            'email_password': data['email_password'],
            'email_provider': data.get('email_provider', 'feishu'),
            'email_count': data.get('email_count', 50)  # 修改默认值为50
        }
        
        logger.info(f"邮件同步配置 - 用户: {config['email_username']}, 数量: {config['email_count']}, 提供商: {config['email_provider']}")
        
        syncer = EmailSyncAction(config)
        
        # 执行同步
        result = syncer.run_sync()
        
        logger.info(f"邮件同步完成: {result}")
        
        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat(),
            'message': '邮件同步完成'
        }), 200
        
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        logger.error(f"邮件同步失败: {error_msg}")
        logger.error(f"错误堆栈: {error_trace}")
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat(),
            'message': '邮件同步失败'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        # 检查模块状态
        module_status = {
            'douyin_syncer_loaded': DouyinVideoSync is not None,
            'email_syncer_loaded': EmailSyncAction is not None
        }
        
        # 两个模块都加载成功才认为服务完全可用
        all_modules_ready = DouyinVideoSync is not None and EmailSyncAction is not None
        
        return jsonify({
            'status': 'ready' if all_modules_ready else 'not_ready',
            'modules': module_status,
            'timestamp': datetime.now().isoformat(),
            'message': '所有配置通过HTTP请求参数传递，无需环境变量配置'
        }), 200
        
    except Exception as e:
        logger.error(f"状态检查失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/providers', methods=['GET'])
def get_supported_providers():
    """获取支持的邮箱提供商列表"""
    try:
        from email_providers import EmailProviderFactory
        providers = EmailProviderFactory.get_supported_providers()
        
        # 提供商详细信息
        provider_details = {
            'lark': {'name': '飞书邮箱', 'server': 'imap.feishu.cn'},
            'feishu': {'name': '飞书邮箱', 'server': 'imap.feishu.cn'},
            'gmail': {'name': 'Gmail', 'server': 'imap.gmail.com'},
            'google': {'name': 'Gmail', 'server': 'imap.gmail.com'},
            'qq': {'name': 'QQ邮箱', 'server': 'imap.qq.com'},
            'netease': {'name': '网易邮箱', 'server': 'imap.163.com'},
            '163': {'name': '网易邮箱', 'server': 'imap.163.com'}
        }
        
        return jsonify({
            'supported_providers': providers,
            'provider_details': {p: provider_details.get(p, {'name': p, 'server': 'unknown'}) for p in providers},
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'获取提供商列表失败: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/debug', methods=['GET'])
def get_debug_info():
    """获取调试信息"""
    try:
        import sys
        import os
        
        return jsonify({
            'python_version': sys.version,
            'current_directory': os.getcwd(),
            'douyin_syncer_loaded': DouyinVideoSync is not None,
            'email_syncer_loaded': EmailSyncAction is not None,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'调试端点错误: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': '接口不存在',
        'message': '请检查请求路径是否正确',
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': '服务器内部错误',
        'message': '请稍后重试或联系管理员',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # 开发环境运行
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"启动Flask应用，端口: {port}, 调试模式: {debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)