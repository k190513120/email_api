# 飞书邮件同步 API

这是一个用于同步飞书邮箱邮件到飞书多维表格的 Python API 服务。

## 功能特性

- 支持多种邮箱提供商（飞书、Gmail、QQ、163、Outlook等）
- 自动同步邮件到飞书多维表格
- RESTful API 接口
- 支持 Docker 部署
- 支持 Koyeb 云平台部署

## API 接口

### 健康检查
```
GET /health
```

### 邮件同步
```
POST /api/sync/email
```

请求参数：
```json
{
  "personal_base_token": "你的飞书个人基础令牌",
  "bitable_url": "多维表格URL",
  "email_username": "邮箱用户名",
  "email_password": "邮箱密码",
  "email_provider": "邮箱提供商（feishu/gmail/qq/163/outlook）",
  "email_count": 50
}
```

### 获取支持的邮箱提供商
```
GET /api/providers
```

## 部署到 Koyeb

1. 将代码推送到 GitHub 仓库
2. 在 Koyeb 控制台创建新应用
3. 连接 GitHub 仓库
4. 使用提供的 `koyeb.yaml` 配置文件
5. 部署应用

## 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app.py
```

应用将在 http://localhost:8000 启动。

## 环境变量

- `PORT`: 应用端口（默认：8000）
- `FLASK_ENV`: Flask 环境（development/production）

## 支持的邮箱提供商

- 飞书邮箱 (feishu)
- Lark 邮箱 (lark)
- Gmail (gmail)
- QQ 邮箱 (qq)
- 163 邮箱 (163)
- Outlook (outlook)