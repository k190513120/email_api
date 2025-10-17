# 支持的邮箱提供商

本服务支持多种邮箱类型，以下是详细的配置说明：

## 支持的邮箱类型

### 1. 飞书邮箱 (Lark Email)

- **标识符**: `lark` 或 `feishu`
- **IMAP服务器**: `imap.feishu.cn`
- **端口**: `993`
- **加密**: SSL/TLS

**配置说明**:
- 可以直接使用飞书账号的登录密码
- 推荐在飞书安全设置中生成应用专用密码以提高安全性

### 2. Gmail

- **标识符**: `gmail` 或 `google`
- **IMAP服务器**: `imap.gmail.com`
- **端口**: `993`
- **加密**: SSL/TLS

**配置说明**:
1. 必须开启两步验证
2. 在Google账户设置中生成应用专用密码
3. 使用应用专用密码而不是账户密码

**设置步骤**:
1. 登录Google账户 → 安全性
2. 开启两步验证
3. 生成应用专用密码
4. 在API请求中使用生成的16位密码

### 3. QQ邮箱

- **标识符**: `qq`
- **IMAP服务器**: `imap.qq.com`
- **端口**: `993`
- **加密**: SSL/TLS

**配置说明**:
1. 登录QQ邮箱网页版
2. 设置 → 账户 → 开启IMAP/SMTP服务
3. 生成授权码
4. 使用授权码而不是QQ密码

### 4. 网易邮箱 (163邮箱)

- **标识符**: `netease` 或 `163`
- **IMAP服务器**: `imap.163.com`
- **端口**: `993`
- **加密**: SSL/TLS

**配置说明**:
1. 登录163邮箱网页版
2. 设置 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启IMAP/SMTP服务
4. 生成授权码
5. 使用授权码而不是邮箱密码

## API使用示例

### 飞书邮箱示例

```json
{
  "email_provider": "lark",
  "email_username": "user@company.feishu.cn",
  "email_password": "your_password_or_app_password"
}
```

### Gmail示例

```json
{
  "email_provider": "gmail",
  "email_username": "user@gmail.com",
  "email_password": "abcd efgh ijkl mnop"
}
```

### QQ邮箱示例

```json
{
  "email_provider": "qq",
  "email_username": "user@qq.com",
  "email_password": "authorization_code"
}
```

### 网易邮箱示例

```json
{
  "email_provider": "netease",
  "email_username": "user@163.com",
  "email_password": "authorization_code"
}
```

## 常见问题

### Q: 为什么连接失败？

**A**: 请检查以下几点：
1. 邮箱类型标识符是否正确
2. 是否已开启IMAP服务
3. 是否使用了正确的授权码/应用专用密码
4. 网络连接是否正常

### Q: Gmail提示"用户名或密码不正确"？

**A**: Gmail需要使用应用专用密码：
1. 确保已开启两步验证
2. 生成应用专用密码（16位，包含空格）
3. 使用应用专用密码而不是Google账户密码

### Q: QQ邮箱连接超时？

**A**: 请确认：
1. 已在QQ邮箱设置中开启IMAP服务
2. 使用的是授权码而不是QQ密码
3. 授权码没有过期

### Q: 如何获取更多邮件？

**A**: 在API请求中设置 `email_count` 参数：
```json
{
  "email_count": 100
}
```

## 扩展支持

如需支持其他邮箱提供商，请在GitHub仓库中提交Issue，包含以下信息：
- 邮箱提供商名称
- IMAP服务器地址和端口
- 认证方式说明
- 使用场景描述

我们会根据需求优先级添加支持。