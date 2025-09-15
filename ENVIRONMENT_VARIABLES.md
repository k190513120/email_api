# 环境变量配置说明

## 概述

飞书邮件同步应用已成功部署到 Koyeb 平台！

**部署信息：**
- 应用名称: `larkemail2`
- 服务名称: `api`
- 访问地址: https://larkemail2-miaomiaocompany-b5ed831e.koyeb.app
- 状态: ✅ HEALTHY

## 重要说明

**此应用无需配置环境变量！** 所有配置参数都通过 HTTP 请求参数传递，这样设计更加灵活和安全。

## API 端点说明

### 1. 健康检查
```bash
GET /health
```

**响应示例：**
```json
{
  "service": "lark-email-sync",
  "status": "healthy",
  "timestamp": "2025-09-15T03:31:08.794823"
}
```

### 2. 服务状态
```bash
GET /api/status
```

**响应示例：**
```json
{
  "message": "所有配置通过HTTP请求参数传递，无需环境变量配置",
  "modules": {
    "douyin_syncer_loaded": false,
    "email_syncer_loaded": false
  },
  "status": "not_ready",
  "timestamp": "2025-09-15T03:31:14.924808"
}
```

### 3. 抖音同步
```bash
POST /api/sync/douyin
Content-Type: application/json
```

**请求参数：**
```json
{
  "douyin_url": "https://www.douyin.com/user/YOUR_USER_ID",
  "bitable_url": "https://your-bitable-url",
  "personal_base_token": "your-feishu-token",
  "sync_count": 5
}
```

**参数说明：**
- `douyin_url`: 抖音用户主页URL
- `bitable_url`: 飞书多维表格URL
- `personal_base_token`: 飞书个人基础Token
- `sync_count`: 同步视频数量（可选，默认5）

### 4. 邮件同步
```bash
POST /api/sync/email
Content-Type: application/json
```

**请求参数：**
```json
{
  "bitable_url": "https://your-bitable-url",
  "personal_base_token": "your-feishu-token",
  "email_username": "your-email@example.com",
  "email_password": "your-email-password",
  "email_provider": "feishu",
  "email_count": 5
}
```

**参数说明：**
- `bitable_url`: 飞书多维表格URL
- `personal_base_token`: 飞书个人基础Token
- `email_username`: 邮箱用户名
- `email_password`: 邮箱密码或应用专用密码
- `email_provider`: 邮件服务提供商（支持：feishu, gmail, outlook等）
- `email_count`: 同步邮件数量（可选，默认5）

## 使用示例

### 测试抖音同步功能
```bash
curl -X POST https://larkemail2-miaomiaocompany-b5ed831e.koyeb.app/api/sync/douyin \
  -H "Content-Type: application/json" \
  -d '{
    "douyin_url": "https://www.douyin.com/user/YOUR_USER_ID",
    "bitable_url": "https://your-bitable-url",
    "personal_base_token": "your-token",
    "sync_count": 5
  }'
```

### 测试邮件同步功能
```bash
curl -X POST https://larkemail2-miaomiaocompany-b5ed831e.koyeb.app/api/sync/email \
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

## 获取必要的配置信息

### 1. 飞书个人基础Token
1. 访问 [飞书开发者后台](https://open.feishu.cn/app)
2. 创建或选择应用
3. 在「凭证与基础信息」中获取 `App Token`
4. 或使用个人基础Token（推荐用于个人使用）

### 2. 飞书多维表格URL
1. 在飞书中创建多维表格
2. 复制表格的分享链接
3. 确保表格权限设置为可编辑

### 3. 邮箱配置
- **飞书邮箱**: 使用飞书账号和密码
- **Gmail**: 需要开启两步验证并生成应用专用密码
- **Outlook**: 使用账号密码或应用密码

## 安全建议

1. **API密钥安全**
   - 不要在公共场所暴露Token
   - 定期轮换API密钥
   - 使用HTTPS传输敏感数据

2. **访问控制**
   - 考虑添加API认证机制
   - 限制访问来源IP（如果需要）
   - 监控异常访问模式

3. **数据保护**
   - 邮箱密码建议使用应用专用密码
   - 定期检查飞书表格权限设置
   - 避免在日志中记录敏感信息

## 故障排除

### 常见错误及解决方案

1. **模块加载失败**
   - 检查请求参数是否完整
   - 确认飞书Token有效性
   - 验证多维表格URL格式

2. **邮件同步失败**
   - 检查邮箱用户名和密码
   - 确认邮件服务商设置
   - 验证网络连接

3. **抖音同步失败**
   - 检查抖音URL格式
   - 确认用户主页可访问
   - 验证同步数量设置

### 查看应用日志
```bash
# 查看运行时日志
koyeb service logs 104eff15

# 查看构建日志
koyeb service logs 104eff15 -t build
```

## 监控和维护

### 定期检查
- 应用健康状态: `GET /health`
- 服务状态: `GET /api/status`
- 资源使用情况（通过Koyeb控制台）

### 性能优化
- 根据使用情况调整实例类型
- 监控响应时间和错误率
- 优化同步频率和数量

## 技术支持

如果遇到问题：
1. 检查API响应和错误信息
2. 查看应用日志
3. 验证请求参数格式
4. 联系技术支持

---

**部署完成！** 🎉

您的飞书邮件同步应用已成功部署到 Koyeb 平台，可以开始使用了！