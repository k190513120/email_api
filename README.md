# 飞书邮件同步 API

一个简洁的 Python Flask API 服务，用于同步邮件数据到飞书多维表格。

## 功能特性

- 支持多种邮箱提供商（Gmail、QQ邮箱、网易邮箱、Outlook、飞书邮箱）
- 自动同步邮件到飞书多维表格
- RESTful API 接口
- Docker 容器化部署
- 支持 Koyeb 云平台部署

## API 接口

### 邮件同步
```
POST /api/sync/email
```

请求参数：
```json
{
  "email_username": "your@email.com",
  "email_password": "your_password",
  "email_provider": "gmail",
  "email_count": 10,
  "personal_base_token": "your_feishu_token",
  "bitable_url": "https://your_feishu_bitable_url"
}
```

### 其他接口
- `GET /health` - 健康检查
- `GET /api/status` - 服务状态
- `GET /api/providers` - 支持的邮箱提供商

## 部署

### Koyeb 部署
1. Fork 此仓库到你的 GitHub 账户
2. 在 Koyeb 控制台创建新的 Web 服务
3. 选择 GitHub 作为部署方式
4. 选择你的仓库和 main 分支
5. 设置运行命令：`gunicorn --bind 0.0.0.0:8000 --workers 2 app:app`
6. 设置端口：8000
7. 部署完成

### 本地开发
```bash
pip install -r requirements.txt
python app.py
```

## 支持的邮箱提供商

- Gmail
- QQ邮箱
- 网易邮箱（163）
- Outlook
- 飞书邮箱

## 注意事项

- 请确保邮箱已开启 IMAP 服务
- 使用应用专用密码而非账户密码
- 飞书 token 需要有多维表格的读写权限