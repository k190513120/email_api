# Render 部署指南

## 项目概述

飞书邮件同步服务是一个基于 Flask 的 Web 应用，提供抖音视频同步和邮件同步功能。本指南将帮助您将应用部署到 Render 平台。

## 功能特性

- ✅ 抖音视频同步到飞书多维表格
- ✅ 邮件同步到飞书多维表格
- ✅ RESTful API 接口
- ✅ 健康检查端点
- ✅ 跨域支持 (CORS)
- ✅ 详细的错误处理和日志记录

## API 端点

### 基础端点
- `GET /` - 服务信息和端点列表
- `GET /health` - 健康检查
- `GET /api/status` - 服务状态和模块加载情况

### 同步端点
- `POST /api/sync/douyin` - 抖音视频同步
- `POST /api/sync/email` - 邮件同步

## 部署前准备

### 1. 确保项目文件完整

确保您的项目包含以下文件：
- `app.py` - 主应用文件
- `requirements.txt` - Python 依赖
- `render.yaml` - Render 配置文件
- `douyin_sync_action.py` - 抖音同步模块
- `email_sync_action.py` - 邮件同步模块

### 2. 验证本地运行

在部署前，请确保应用在本地正常运行：

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python app.py

# 测试健康检查
curl http://localhost:8000/health

# 检查服务状态
curl http://localhost:8000/api/status
```

## Render 部署步骤

### 方法一：通过 GitHub 连接（推荐）

1. **准备 GitHub 仓库**
   - 将项目代码推送到 GitHub 仓库
   - 确保 `render.yaml` 文件在根目录

2. **连接 Render**
   - 访问 [Render Dashboard](https://dashboard.render.com/)
   - 点击 "New" → "Web Service"
   - 选择 "Build and deploy from a Git repository"
   - 连接您的 GitHub 账户并选择项目仓库

3. **配置服务**
   - **Name**: `lark-email-sync`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Plan**: 选择合适的计划（Free 计划可用于测试）

4. **环境变量设置**
   ```
   FLASK_ENV=production
   ```

5. **部署**
   - 点击 "Create Web Service"
   - Render 将自动构建和部署您的应用

### 方法二：使用 render.yaml 配置文件

如果您的项目包含 `render.yaml` 文件，Render 将自动使用该配置：

1. 连接 GitHub 仓库到 Render
2. Render 会自动检测 `render.yaml` 并应用配置
3. 无需手动配置服务设置

## 部署后验证

### 1. 检查部署状态

在 Render Dashboard 中：
- 查看部署日志确保无错误
- 确认服务状态为 "Live"

### 2. 测试 API 端点

使用您的 Render 应用 URL（例如：`https://your-app-name.onrender.com`）：

```bash
# 健康检查
curl https://your-app-name.onrender.com/health

# 服务状态
curl https://your-app-name.onrender.com/api/status

# 服务信息
curl https://your-app-name.onrender.com/
```

### 3. 测试同步功能

#### 抖音视频同步测试
```bash
curl -X POST https://your-app-name.onrender.com/api/sync/douyin \
  -H "Content-Type: application/json" \
  -d '{
    "douyin_url": "https://www.douyin.com/user/your-user-id",
    "bitable_url": "https://your-bitable-url",
    "personal_base_token": "your-token",
    "sync_count": 10
  }'
```

#### 邮件同步测试
```bash
curl -X POST https://your-app-name.onrender.com/api/sync/email \
  -H "Content-Type: application/json" \
  -d '{
    "personal_base_token": "your-token",
    "bitable_url": "https://your-bitable-url"
  }'
```

## 常见问题解决

### 1. 构建失败

**问题**: 依赖安装失败
**解决方案**:
- 检查 `requirements.txt` 文件格式
- 确保所有依赖版本兼容
- 查看构建日志中的具体错误信息

### 2. 应用启动失败

**问题**: 应用无法启动
**解决方案**:
- 检查 `app.py` 中的语法错误
- 确保所有必需的模块文件存在
- 查看应用日志中的错误信息

### 3. 模块导入失败

**问题**: `douyin_sync_action` 或 `email_sync_action` 导入失败
**解决方案**:
- 确保模块文件存在于项目根目录
- 检查模块文件中的语法错误
- 验证模块依赖是否正确安装

### 4. API 请求失败

**问题**: 同步 API 返回错误
**解决方案**:
- 检查请求参数是否完整
- 验证飞书 token 是否有效
- 确认多维表格 URL 格式正确

## 监控和维护

### 1. 日志监控

在 Render Dashboard 中：
- 定期查看应用日志
- 关注错误和警告信息
- 监控应用性能指标

### 2. 健康检查

设置定期健康检查：
```bash
# 创建监控脚本
echo '#!/bin/bash
curl -f https://your-app-name.onrender.com/health || exit 1' > health_check.sh
chmod +x health_check.sh
```

### 3. 自动部署

配置自动部署：
- 在 Render 中启用 "Auto-Deploy"
- 每次推送到 main 分支时自动部署
- 设置部署通知

## 扩展和优化

### 1. 性能优化

- 使用更高级的 Render 计划获得更好性能
- 考虑添加缓存机制
- 优化数据库查询（如果使用）

### 2. 安全增强

- 添加 API 认证机制
- 实施请求频率限制
- 使用 HTTPS 加密通信

### 3. 功能扩展

- 添加更多同步源
- 实现批量操作
- 添加数据验证和清理功能

## 支持和帮助

如果在部署过程中遇到问题：

1. 查看 Render 官方文档：https://render.com/docs
2. 检查应用日志获取详细错误信息
3. 验证本地环境是否正常工作
4. 确认所有配置文件格式正确

---

**注意**: 请确保在生产环境中保护好您的 API 密钥和敏感信息，不要将它们硬编码在代码中。