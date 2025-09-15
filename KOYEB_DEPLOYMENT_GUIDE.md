# Koyeb 部署指南

## 概述
本指南将帮助您在 Koyeb 平台上重新创建和部署飞书邮件同步应用。

## 前置条件

1. **Koyeb 账户**: 确保您已注册 Koyeb 账户
2. **GitHub 仓库**: 代码已推送到 GitHub 仓库
3. **飞书应用配置**: 准备好飞书个人基础Token和多维表格URL

## 部署步骤

### 1. 登录 Koyeb 控制台

访问 [Koyeb 控制台](https://app.koyeb.com/) 并登录您的账户。

### 2. 创建新应用

1. 点击 "Create App" 按钮
2. 选择 "GitHub" 作为部署源
3. 连接您的 GitHub 账户（如果尚未连接）
4. 选择包含此项目的仓库

### 3. 配置应用设置

#### 基本配置
- **App name**: `lark-email-sync-v2` (或您喜欢的名称)
- **Branch**: `main` (或您的主分支)
- **Build method**: `Dockerfile`
- **Dockerfile path**: `Dockerfile`

#### 服务配置
- **Service name**: `web`
- **Port**: `8000`
- **Instance type**: `Nano` (512MB RAM, 0.1 CPU)
- **Regions**: 选择离您最近的区域（推荐 `fra` 法兰克福）

#### 高级设置
- **Health check path**: `/health`
- **Health check port**: `8000`
- **Health check initial delay**: `30s`
- **Health check timeout**: `10s`
- **Health check interval**: `30s`
- **Health check retries**: `3`

### 4. 环境变量配置（可选）

由于应用设计为通过HTTP请求参数传递配置，您无需设置环境变量。但如果需要，可以添加：

```
FLASK_ENV=production
PYTHONUNBUFFERED=1
```

### 5. 部署应用

1. 检查所有配置无误后，点击 "Deploy" 按钮
2. 等待构建和部署完成（通常需要 3-5 分钟）
3. 部署成功后，您将获得一个公共URL

## 验证部署

### 1. 健康检查
```bash
curl https://your-app-url.koyeb.app/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "lark-email-sync"
}
```

### 2. 服务状态检查
```bash
curl https://your-app-url.koyeb.app/api/status
```

预期响应：
```json
{
  "status": "ready",
  "modules": {
    "douyin_syncer_loaded": true,
    "email_syncer_loaded": true
  },
  "timestamp": "2024-01-15T10:30:00.000Z",
  "message": "所有配置通过HTTP请求参数传递，无需环境变量配置"
}
```

### 3. 测试抖音同步功能
```bash
curl -X POST https://your-app-url.koyeb.app/api/sync/douyin \
  -H "Content-Type: application/json" \
  -d '{
    "douyin_url": "https://www.douyin.com/user/YOUR_USER_ID",
    "bitable_url": "https://your-bitable-url",
    "personal_base_token": "your-token",
    "sync_count": 5
  }'
```

### 4. 测试邮件同步功能
```bash
curl -X POST https://your-app-url.koyeb.app/api/sync/email \
  -H "Content-Type: application/json" \
  -d '{
    "bitable_url": "https://your-bitable-url",
    "personal_base_token": "your-token",
    "email_username": "your-email@example.com",
    "email_password": "your-password",
    "email_provider": "feishu",
    "email_count": 5
  }'
```

## 故障排除

### 常见问题

1. **构建失败**
   - 检查 Dockerfile 语法
   - 确保 requirements.txt 中的依赖包可用
   - 查看构建日志获取详细错误信息

2. **健康检查失败**
   - 确保应用在端口 8000 上运行
   - 检查 `/health` 端点是否可访问
   - 增加健康检查的初始延迟时间

3. **模块加载失败**
   - 检查 Python 版本兼容性
   - 确保所有依赖包已正确安装
   - 查看应用日志获取详细错误信息

### 查看日志

在 Koyeb 控制台中：
1. 进入您的应用
2. 点击 "Logs" 标签
3. 查看实时日志或历史日志

### 重新部署

如果需要重新部署：
1. 在 Koyeb 控制台中进入您的应用
2. 点击 "Redeploy" 按钮
3. 或者推送新代码到 GitHub，触发自动部署

## 配置优化建议

### 1. 资源配置
- 对于轻量使用：Nano 实例（512MB RAM）
- 对于中等使用：Small 实例（1GB RAM）
- 对于重度使用：Medium 实例（2GB RAM）

### 2. 区域选择
- 选择离您的用户最近的区域
- 推荐区域：`fra`（法兰克福）、`sin`（新加坡）

### 3. 自动扩缩容
- 最小实例数：1
- 最大实例数：根据需求调整（建议不超过3）

## 安全注意事项

1. **API 密钥安全**
   - 不要在代码中硬编码敏感信息
   - 使用 HTTPS 传输敏感数据
   - 定期轮换 API 密钥

2. **访问控制**
   - 考虑添加 API 认证
   - 限制访问来源 IP（如果需要）
   - 监控异常访问模式

## 监控和维护

1. **定期检查**
   - 监控应用健康状态
   - 查看错误日志
   - 检查资源使用情况

2. **更新维护**
   - 定期更新依赖包
   - 关注安全补丁
   - 备份重要配置

## 支持

如果遇到问题：
1. 查看 Koyeb 官方文档
2. 检查应用日志
3. 联系技术支持

---

**注意**: 请根据您的具体需求调整配置参数。此指南基于当前的应用架构和 Koyeb 平台特性。