# Render 快速部署步骤

## 🚀 一键部署指南

### 步骤 1: 准备代码仓库

```bash
# 1. 确保所有文件都已提交到 Git
git add .
git commit -m "准备 Render 部署"
git push origin main
```

### 步骤 2: 在 Render 创建服务

1. 访问 [Render Dashboard](https://dashboard.render.com/)
2. 点击 **"New"** → **"Web Service"**
3. 选择 **"Build and deploy from a Git repository"**
4. 连接您的 GitHub 仓库

### 步骤 3: 配置服务设置

**基本设置:**
- **Name**: `lark-email-sync`
- **Environment**: `Python 3`
- **Region**: 选择最近的区域
- **Branch**: `main`

**构建设置:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

**环境变量:**
```
FLASK_ENV=production
```

### 步骤 4: 部署

1. 点击 **"Create Web Service"**
2. 等待构建和部署完成（通常需要 2-5 分钟）
3. 部署成功后，您将获得一个 `.onrender.com` 的 URL

### 步骤 5: 验证部署

使用您的 Render URL 测试以下端点：

```bash
# 替换 YOUR_APP_URL 为您的实际 URL
export APP_URL="https://your-app-name.onrender.com"

# 健康检查
curl $APP_URL/health

# 服务状态
curl $APP_URL/api/status

# 应该返回两个模块都已加载:
# {"modules":{"douyin_syncer_loaded":true,"email_syncer_loaded":true},"status":"ready"}
```

## 🔧 使用 API

### 抖音视频同步

```bash
curl -X POST $APP_URL/api/sync/douyin \
  -H "Content-Type: application/json" \
  -d '{
    "douyin_url": "https://www.douyin.com/user/MS4wLjABAAAA...",
    "bitable_url": "https://bytedance.feishu.cn/base/...",
    "personal_base_token": "your-token-here",
    "sync_count": 15
  }'
```

### 邮件同步

```bash
curl -X POST $APP_URL/api/sync/email \
  -H "Content-Type: application/json" \
  -d '{
    "personal_base_token": "your-token-here",
    "bitable_url": "https://bytedance.feishu.cn/base/..."
  }'
```

## 📋 部署检查清单

- [ ] 代码已推送到 GitHub
- [ ] `render.yaml` 文件存在
- [ ] `requirements.txt` 包含所有依赖
- [ ] 本地测试通过
- [ ] Render 服务创建成功
- [ ] 构建日志无错误
- [ ] 健康检查端点响应正常
- [ ] 状态端点显示两个模块都已加载
- [ ] API 端点测试成功

## 🚨 常见问题快速解决

### 构建失败
```bash
# 检查依赖是否正确
pip install -r requirements.txt
```

### 模块导入失败
```bash
# 确保文件存在
ls -la *.py
# 应该看到: app.py, douyin_sync_action.py, email_sync_action.py
```

### 服务无法启动
```bash
# 本地测试启动命令
gunicorn --bind 0.0.0.0:8000 app:app
```

## 📞 获取帮助

如果遇到问题：
1. 查看 Render Dashboard 中的部署日志
2. 检查 `RENDER_DEPLOYMENT_GUIDE.md` 获取详细说明
3. 确认本地环境工作正常

---

**🎉 部署成功后，您的飞书邮件同步服务就可以在云端 24/7 运行了！**