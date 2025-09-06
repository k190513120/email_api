# 邮件同步到飞书多维表格 - GitHub Actions

这个项目提供了一个GitHub Actions工作流，可以自动从邮箱获取邮件并同步到飞书多维表格中。

## 功能特性

- 🔄 自动从IMAP邮箱获取邮件
- 📊 同步邮件数据到飞书多维表格

- 🎯 支持多种邮箱服务商（飞书、Gmail、Outlook、QQ、163、126等）
- 📝 详细的同步日志记录
- 🚀 完全基于GitHub Actions运行，无需服务器

## 快速开始

### 1. 准备工作

#### 1.1 获取飞书多维表格信息

1. 在飞书中创建或打开一个多维表格
2. 复制多维表格的URL，格式类似：`https://example.feishu.cn/base/bascnxxx?table=tblxxx`
3. 在飞书开放平台创建应用，获取 `App Token` 和 `Personal Base Token`

#### 1.2 准备邮箱授权

- **飞书邮箱**: 使用邮箱密码或应用专用密码
- **Gmail**: 需要开启两步验证并生成应用专用密码
- **其他邮箱**: 通常需要开启IMAP服务并使用授权码



### 2. 使用GitHub Actions

#### 2.1 Fork或下载此仓库

将此仓库fork到你的GitHub账号，或者下载代码到你的仓库中。

#### 2.2 运行工作流

1. 进入你的GitHub仓库
2. 点击 `Actions` 标签
3. 选择 `Email to Feishu Bitable Sync` 工作流
4. 点击 `Run workflow` 按钮
5. 填入以下参数：

| 参数名 | 描述 | 示例 |
|--------|------|------|
| 飞书多维表格URL | 多维表格的完整URL | `https://example.feishu.cn/base/bascnxxx?table=tblxxx` |
| 飞书应用Token | 飞书开放平台应用的Token | `cli_a1b2c3d4e5f6...` |
| 飞书个人基础Token | 个人基础Token | `u-7g8h9i0j1k2l...` |
| 邮箱用户名 | 邮箱完整地址 | `user@example.com` |
| 邮箱授权码 | 邮箱密码或授权码 | `your_password_or_auth_code` |
| 邮箱服务商 | 选择邮箱服务商 | `feishu`, `gmail`, `outlook` 等 |

| 获取邮件数量 | 要同步的邮件数量 | `10` (默认) |

6. 点击 `Run workflow` 开始执行

### 3. 查看结果

#### 3.1 GitHub Actions日志

在Actions页面可以查看详细的执行日志，包括：
- 邮箱连接状态
- 邮件获取进度
- 飞书同步结果
- 错误信息（如果有）

#### 3.2 下载结果文件

工作流执行完成后，会生成以下文件供下载：
- `sync_result.json`: 同步结果详情
- `sync_logs.json`: 详细的执行日志



## 多维表格字段说明

同步到飞书多维表格的字段包括：

| 字段名 | 类型 | 描述 |
|--------|------|------|
| 主题 | 文本 | 邮件主题 |
| 发件人 | 文本 | 发件人邮箱地址 |
| 收件人 | 文本 | 收件人邮箱地址 |
| 日期 | 文本 | 邮件发送日期 |
| 正文 | 文本 | 邮件正文内容（限制1000字符） |
| 邮件ID | 文本 | 邮件的唯一标识 |
| 同步时间 | 文本 | 数据同步的时间戳 |

## 本地测试

### 测试邮箱连接

```bash
python3 imap_email_test.py
```



### 完整流程测试

```bash
# 设置环境变量
export BITABLE_URL="your_bitable_url"
export APP_TOKEN="your_app_token"
export PERSONAL_BASE_TOKEN="your_personal_token"
export EMAIL_USERNAME="your_email"
export EMAIL_PASSWORD="your_password"
export EMAIL_PROVIDER="feishu"

export EMAIL_COUNT="5"

# 运行同步脚本
python3 email_sync_action.py
```

## 故障排除

### 常见问题

1. **邮箱连接失败**
   - 检查邮箱用户名和密码是否正确
   - 确认已开启IMAP服务
   - 对于Gmail等邮箱，需要使用应用专用密码

2. **飞书同步失败**
   - 检查多维表格URL格式是否正确
   - 确认App Token和Personal Base Token有效
   - 检查应用是否有多维表格的访问权限



### 调试技巧

1. 先使用较小的邮件数量（如1-2封）进行测试
2. 查看GitHub Actions的详细日志
3. 下载并检查生成的结果文件


## 安全注意事项

1. **不要在代码中硬编码敏感信息**：所有敏感信息都通过GitHub Actions的输入参数传递
2. **使用授权码而非密码**：对于支持的邮箱服务，建议使用应用专用密码或授权码
3. **限制飞书应用权限**：只授予必要的多维表格访问权限


## 技术架构

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   GitHub        │    │   IMAP邮箱       │    │   飞书多维表格   │
│   Actions       │───▶│   服务器         │───▶│   (Bitable)     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                               │

```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！