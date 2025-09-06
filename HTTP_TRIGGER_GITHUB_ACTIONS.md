# 通过HTTP触发GitHub Actions执行邮件同步

本文档说明如何通过HTTP请求触发GitHub Actions来执行邮件同步任务，无需运行独立的服务器。

## 概述

GitHub Actions workflow已配置为支持两种触发方式：
1. **手动触发** (`workflow_dispatch`) - 通过GitHub网页界面手动触发
2. **HTTP触发** (`repository_dispatch`) - 通过GitHub API的HTTP请求触发

## 前置条件

### 1. 获取GitHub Personal Access Token

1. 访问 GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 设置token名称和过期时间
4. 选择以下权限：
   - `repo` (完整仓库访问权限)
   - `workflow` (更新GitHub Actions workflows)
5. 生成并保存token

### 2. 仓库信息

- **仓库所有者**: `k190513120`
- **仓库名称**: `lark_email`
- **完整仓库路径**: `k190513120/lark_email`

## HTTP触发方式

### API端点

```
POST https://api.github.com/repos/k190513120/lark_email/dispatches
```

### 请求头

```
Authorization: Bearer YOUR_GITHUB_TOKEN
Accept: application/vnd.github.v3+json
Content-Type: application/json
```

### 请求体格式

```json
{
  "event_type": "email-sync",
  "client_payload": {
    "bitable_url": "飞书多维表格URL",
    "app_token": "飞书应用Token",
    "personal_base_token": "飞书个人基础Token",
    "email_username": "邮箱用户名",
    "email_password": "邮箱授权码",
    "email_provider": "邮箱服务商",
    "email_count": "获取邮件数量"
  }
}
```

### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `bitable_url` | string | 是 | - | 飞书多维表格的完整URL |
| `app_token` | string | 是 | - | 飞书应用的Token |
| `personal_base_token` | string | 是 | - | 飞书个人基础Token |
| `email_username` | string | 是 | - | 邮箱用户名 |
| `email_password` | string | 是 | - | 邮箱授权码（不是登录密码） |
| `email_provider` | string | 否 | feishu | 邮箱服务商：feishu/gmail/outlook/qq/163/126 |
| `email_count` | string | 否 | 10 | 获取的邮件数量 |

## 使用示例

### 1. 使用curl命令

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "email-sync",
    "client_payload": {
      "bitable_url": "https://your-feishu-bitable-url",
      "app_token": "your-app-token",
      "personal_base_token": "your-personal-base-token",
      "email_username": "your-email@example.com",
      "email_password": "your-email-auth-code",
      "email_provider": "gmail",
      "email_count": "20"
    }
  }' \
  https://api.github.com/repos/k190513120/lark_email/dispatches
```

### 2. 使用Python requests

```python
import requests
import json

# GitHub配置
GITHUB_TOKEN = "your_github_token_here"
REPO_OWNER = "k190513120"
REPO_NAME = "lark_email"

# API端点
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"

# 请求头
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json"
}

# 请求数据
data = {
    "event_type": "email-sync",
    "client_payload": {
        "bitable_url": "https://your-feishu-bitable-url",
        "app_token": "your-app-token",
        "personal_base_token": "your-personal-base-token",
        "email_username": "your-email@example.com",
        "email_password": "your-email-auth-code",
        "email_provider": "gmail",
        "email_count": "20"
    }
}

# 发送请求
response = requests.post(url, headers=headers, json=data)

if response.status_code == 204:
    print("✅ GitHub Actions workflow triggered successfully!")
    print("Check the Actions tab in your GitHub repository to see the running workflow.")
else:
    print(f"❌ Failed to trigger workflow. Status code: {response.status_code}")
    print(f"Response: {response.text}")
```

### 3. 使用JavaScript fetch

```javascript
const triggerEmailSync = async () => {
  const GITHUB_TOKEN = 'your_github_token_here';
  const REPO_OWNER = 'k190513120';
  const REPO_NAME = 'lark_email';
  
  const url = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/dispatches`;
  
  const data = {
    event_type: 'email-sync',
    client_payload: {
      bitable_url: 'https://your-feishu-bitable-url',
      app_token: 'your-app-token',
      personal_base_token: 'your-personal-base-token',
      email_username: 'your-email@example.com',
      email_password: 'your-email-auth-code',
      email_provider: 'gmail',
      email_count: '20'
    }
  };
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (response.status === 204) {
      console.log('✅ GitHub Actions workflow triggered successfully!');
      console.log('Check the Actions tab in your GitHub repository to see the running workflow.');
    } else {
      console.error(`❌ Failed to trigger workflow. Status code: ${response.status}`);
      const errorText = await response.text();
      console.error(`Response: ${errorText}`);
    }
  } catch (error) {
    console.error('❌ Error triggering workflow:', error);
  }
};

// 调用函数
triggerEmailSync();
```

## 响应说明

### 成功响应
- **状态码**: `204 No Content`
- **说明**: workflow已成功触发，无响应体

### 错误响应
- **状态码**: `401 Unauthorized` - Token无效或权限不足
- **状态码**: `404 Not Found` - 仓库不存在或无访问权限
- **状态码**: `422 Unprocessable Entity` - 请求格式错误

## 监控执行状态

### 1. 通过GitHub网页界面
1. 访问仓库页面：`https://github.com/k190513120/lark_email`
2. 点击 "Actions" 标签页
3. 查看最新的workflow运行状态

### 2. 通过GitHub API查询

```bash
# 获取最新的workflow运行状态
curl -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/k190513120/lark_email/actions/runs
```

## 安全注意事项

1. **保护GitHub Token**：
   - 不要在代码中硬编码token
   - 使用环境变量或安全的配置管理
   - 定期轮换token

2. **保护敏感参数**：
   - 邮箱密码使用授权码，不是登录密码
   - 飞书token具有敏感权限，请妥善保管

3. **访问控制**：
   - 确保GitHub token具有最小必要权限
   - 定期审查token的使用情况

## 优势对比

### HTTP触发GitHub Actions vs 独立Flask服务

| 特性 | GitHub Actions | Flask服务 |
|------|----------------|----------|
| **服务器成本** | 免费（有限额度） | 需要服务器资源 |
| **维护成本** | 低（GitHub托管） | 高（需要维护服务器） |
| **可扩展性** | 自动扩展 | 需要手动扩展 |
| **安全性** | GitHub安全保障 | 需要自行保障 |
| **日志记录** | 内置日志系统 | 需要自行实现 |
| **监控告警** | GitHub通知 | 需要自行实现 |
| **部署复杂度** | 无需部署 | 需要部署和配置 |

## 故障排除

### 常见问题

1. **401 Unauthorized**
   - 检查GitHub token是否正确
   - 确认token具有repo和workflow权限

2. **404 Not Found**
   - 确认仓库路径正确：`k190513120/lark_email`
   - 检查token是否有访问该仓库的权限

3. **Workflow未执行**
   - 确认`event_type`为`email-sync`
   - 检查workflow文件中的触发器配置

4. **参数传递问题**
   - 确认所有必填参数都已提供
   - 检查参数格式是否正确

### 调试建议

1. 先使用curl命令测试基本功能
2. 检查GitHub Actions页面的执行日志
3. 确认所有环境变量都正确传递
4. 验证飞书和邮箱的配置参数

## 总结

通过HTTP触发GitHub Actions是一个优雅的解决方案，它：
- ✅ 无需维护独立服务器
- ✅ 利用GitHub的免费计算资源
- ✅ 提供完整的日志和监控
- ✅ 具有良好的安全性和可靠性
- ✅ 支持灵活的参数传递

这种方式特别适合定期执行的任务，如邮件同步，既经济又可靠。