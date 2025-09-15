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

# 暂时禁用邮件同步模块
# try:
#     from email_sync_action import EmailSyncAction
# except ImportError as e:
#     print(f"导入邮件同步模块错误: {e}")
#     EmailSyncAction = None
EmailSyncAction = None  # 暂时禁用邮件同步功能

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

# 暂时禁用邮件同步端点
# @app.route('/api/sync/email', methods=['POST'])
# def sync_emails():
#     """触发邮件同步"""
#     return jsonify({
#         'success': False,
#         'error': '邮件同步功能暂时禁用',
#         'timestamp': datetime.now().isoformat()
#     }), 503

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取服务状态"""
    try:
        # 检查模块状态（只检查抖音模块）
        module_status = {
            'douyin_syncer_loaded': DouyinVideoSync is not None,
            'email_syncer_loaded': False  # 暂时禁用
        }
        
        # 只要抖音模块加载成功就认为服务可用
        all_modules_ready = DouyinVideoSync is not None
        
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

@app.route('/api/debug', methods=['GET'])
def get_debug_info():
    """获取调试信息"""
    try:
        import sys
        import os
        
        debug_info = {
            'python_version': sys.version,
            'current_directory': os.getcwd(),
            'python_path': sys.path[:5],  # 显示前5个路径
            'douyin_syncer_loaded': DouyinVideoSync is not None,
            'email_syncer_loaded': False,
            'files_in_directory': [],
            'import_errors': []
        }
        
        # 列出当前目录的文件
        try:
            debug_info['files_in_directory'] = [f for f in os.listdir('.') if f.endswith('.py')][:10]
        except Exception as e:
            debug_info['files_in_directory'] = [f'Error listing files: {e}']
        
        # 测试导入
        try:
            import requests
            debug_info['requests_available'] = True
        except Exception as e:
            debug_info['requests_available'] = False
            debug_info['import_errors'].append(f'requests: {e}')
        
        try:
            from baseopensdk import BaseClient
            debug_info['baseopensdk_available'] = True
        except Exception as e:
            debug_info['baseopensdk_available'] = False
            debug_info['import_errors'].append(f'baseopensdk: {e}')
        
        try:
            from douyin_sync_action import DouyinVideoSync as TestDouyinVideoSync
            debug_info['douyin_sync_action_available'] = True
        except Exception as e:
            debug_info['douyin_sync_action_available'] = False
            debug_info['import_errors'].append(f'douyin_sync_action: {e}')
        
        return jsonify(debug_info)
        
    except Exception as e:
        logger.error(f"调试端点错误: {str(e)}")
        logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({
            'error': f'调试端点内部错误: {str(e)}',
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