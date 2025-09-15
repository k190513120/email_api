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
    from douyin_sync_action import DouyinVideoSync
except ImportError as e:
    print(f"导入抖音同步模块错误: {e}")
    DouyinVideoSync = None

try:
    from email_sync_action import EmailSyncAction
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
            'status': '/api/status'
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
        force_sync = data.get('force', False)
        
        logger.info(f"开始抖音视频同步，强制同步: {force_sync}")
        
        # 创建同步器实例
        syncer = DouyinVideoSync()
        
        # 执行同步
        result = syncer.sync_videos()
        
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
        
        logger.info("开始邮件同步")
        
        # 创建同步器实例
        syncer = EmailSyncAction()
        
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
        # 检查环境变量
        env_status = {
            'FEISHU_APP_ID': bool(os.getenv('FEISHU_APP_ID')),
            'FEISHU_APP_SECRET': bool(os.getenv('FEISHU_APP_SECRET')),
            'DOUYIN_CLIENT_KEY': bool(os.getenv('DOUYIN_CLIENT_KEY')),
            'DOUYIN_CLIENT_SECRET': bool(os.getenv('DOUYIN_CLIENT_SECRET')),
            'DOUYIN_ACCESS_TOKEN': bool(os.getenv('DOUYIN_ACCESS_TOKEN')),
            'FEISHU_BITABLE_APP_TOKEN': bool(os.getenv('FEISHU_BITABLE_APP_TOKEN')),
            'FEISHU_BITABLE_TABLE_ID': bool(os.getenv('FEISHU_BITABLE_TABLE_ID')),
            'BITABLE_URL': bool(os.getenv('BITABLE_URL')),
            'PERSONAL_BASE_TOKEN': bool(os.getenv('PERSONAL_BASE_TOKEN')),
            'EMAIL_USERNAME': bool(os.getenv('EMAIL_USERNAME')),
            'EMAIL_PASSWORD': bool(os.getenv('EMAIL_PASSWORD')),
            'EMAIL_PROVIDER': bool(os.getenv('EMAIL_PROVIDER')),
            'EMAIL_COUNT': bool(os.getenv('EMAIL_COUNT'))
        }
        
        # 检查模块状态
        module_status = {
            'douyin_syncer_loaded': DouyinVideoSync is not None,
            'email_syncer_loaded': EmailSyncAction is not None
        }
        
        all_env_ready = all(env_status.values())
        all_modules_ready = all(module_status.values())
        
        return jsonify({
            'status': 'ready' if (all_env_ready and all_modules_ready) else 'not_ready',
            'environment': env_status,
            'modules': module_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"状态检查失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e),
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