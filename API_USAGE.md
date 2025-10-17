# 邮件同步HTTP API使用说明

## 概述

本API服务提供HTTP接口来触发邮件同步到飞书多维表格的功能。通过POST请求发送邮件配置参数，即可启动邮件同步任务。

## 启动API服务器

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python email_sync_api.py
```

默认启动在 `http://0.0.0.0:5000`

### 3. 自定义配置

可以通过环境变量自定义服务器配置：

```bash
export API_HOST=127.0.0.1
export API_PORT=8080
export API_DEBUG=true
python email_sync_api.py
```

## API接口

### 1. 服务信息

**GET /** 

获取API服务基本信息

**响应示例：**
```json
{
  "service": "邮件同步到飞书多维表格 API",
  "version": "1.0.0",
  "endpoints": {
    "POST /sync": "触发邮件同步",
    "GET /health": "健康检查",
    "GET /": "服务信息"
  },
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 2. 健康检查

**GET /health**

检查API服务状态

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

### 3. 邮件同步

**POST /sync**

触发邮件同步任务

**请求头：**
```
Content-Type: application/json
```

**请求参数：**

| 参数名 | 类型 | 必需 | 说明 |
|--------|------|------|------|
| bitable_url | string | 是 | 飞书多维表格URL |
| personal_base_token | string | 是 | 飞书个人基础令牌 |
| email_username | string | 是 | 邮箱用户名 |
| email_password | string | 是 | 邮箱密码或应用专用密码 |
| email_provider | string | 否 | 邮箱类型，支持: lark, feishu, gmail, google, qq, netease, 163，默认为"feishu" |
| email_count | integer | 否 | 获取邮件数量，默认为50 |

**请求示例：**
```json
{
  "bitable_url": "https://example.feishu.cn/base/bascnxxx",
  "personal_base_token": "pat_xxx",
  "email_username": "your-email@example.com",
  "email_password": "your-password",
  "email_provider": "gmail",
  "email_count": 30
}
```

**成功响应示例：**
```json
{
  "success": true,
  "message": "邮件同步完成",
  "synced_count": 5,
  "skipped_count": 2,
  "total_emails": 7,
  "timestamp": "2024-01-15T10:30:00.123456",
  "logs": [
    "开始获取邮件...",
    "找到7封邮件",
    "同步5封新邮件到飞书多维表格",
    "跳过2封已存在的邮件"
  ]
}
```

**错误响应示例：**
```json
{
  "success": false,
  "error": "缺少必需参数: bitable_url, personal_base_token",
  "timestamp": "2024-01-15T10:30:00.123456"
}
```

## 使用示例

### 使用curl命令

```bash
curl -X POST http://localhost:5000/sync \
  -H "Content-Type: application/json" \
  -d '{
    "bitable_url": "https://example.feishu.cn/base/bascnxxx",
    "personal_base_token": "pat_xxx",
    "email_username": "your-email@example.com",
    "email_password": "your-password",
    "email_provider": "qq",
    "email_count": 25
  }'
```

### 使用Python requests

```python
import requests
import json

url = "http://localhost:5000/sync"
data = {
    "bitable_url": "https://example.feishu.cn/base/bascnxxx",
    "personal_base_token": "pat_xxx",
    "email_username": "your-email@example.com",
    "email_password": "your-password",
    "email_provider": "netease",
    "email_count": 20
}

response = requests.post(url, json=data)
result = response.json()

if result.get('success'):
    print(f"同步成功: {result['message']}")
    print(f"同步邮件数: {result['synced_count']}")
else:
    print(f"同步失败: {result['error']}")
```

### 使用JavaScript fetch

```javascript
const syncEmails = async () => {
  const response = await fetch('http://localhost:5000/sync', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      bitable_url: 'https://example.feishu.cn/base/bascnxxx',
      personal_base_token: 'pat_xxx',
      email_username: 'your-email@example.com',
      email_password: 'your-password',
      email_provider: 'gmail',
      email_count: 15
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log(`同步成功: ${result.message}`);
    console.log(`同步邮件数: ${result.synced_count}`);
  } else {
    console.error(`同步失败: ${result.error}`);
  }
};

syncEmails();
```

## 错误处理

### 常见错误码

- **400 Bad Request**: 请求参数错误或缺少必需参数
- **500 Internal Server Error**: 服务器内部错误，如邮件服务器连接失败、飞书API调用失败等

### 错误排查

1. **参数验证失败**: 检查所有必需参数是否提供且格式正确
2. **邮件服务器连接失败**: 检查邮箱用户名、密码和邮件提供商配置
3. **飞书API调用失败**: 检查飞书多维表格URL和个人基础令牌是否正确
4. **网络连接问题**: 确保服务器能够访问邮件服务器和飞书API

## 安全注意事项

1. **敏感信息保护**: 邮箱密码和飞书令牌等敏感信息通过HTTPS传输
2. **访问控制**: 建议在生产环境中添加身份验证和访问控制
3. **日志安全**: API不会在日志中记录敏感信息如密码和令牌
4. **环境隔离**: 建议在独立的服务器或容器中运行API服务

## 部署建议

### Docker部署

创建Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "email_sync_api.py"]
```

构建和运行:
```bash
docker build -t email-sync-api .
docker run -p 5000:5000 email-sync-api
```

### 生产环境部署

建议使用WSGI服务器如Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 email_sync_api:app
```

## 监控和日志

API服务会输出详细的日志信息，包括：
- 请求处理日志
- 邮件同步进度
- 错误信息和堆栈跟踪

建议在生产环境中配置日志收集和监控系统。