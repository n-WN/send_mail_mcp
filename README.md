# MCP-邮件发送工具

这是一个基于 FastMCP 框架实现的邮件发送工具，可以让你通过简单的API接口发送包含附件的邮件。

## 功能特点

- 📧 支持发送纯文本或HTML格式邮件
- 📎 支持添加多个附件
- 👥 支持多收件人
- 🔒 支持SSL/TLS加密连接
- 🔧 通过环境变量轻松配置

## 安装要求

```bash
uv pip install fastmcp python-dotenv
```

## 快速开始

1. 创建`.env`文件并配置邮箱信息：

```
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=your_email@example.com
SMTP_PASS=your_password_or_app_password
DEFAULT_FROM_NAME=Your Name
DEFAULT_FROM_EMAIL=your_email@example.com
```

2. 运行服务器：

```bash
python server.py
```

> 安装到 Claude desktop app

```sh
fastmcp install server.py
```

3. 服务启动后，可以通过FastMCP客户端或界面调用邮件发送工具。

## 工具函数

### `send_email_with_attachment`

发送带有附件的邮件。

**参数:**
- `to_emails`: 收件人邮箱地址列表
- `subject`: 邮件主题
- `body`: 邮件正文
- `attachment_paths`(可选): 附件文件路径列表
- `body_type`(可选): 邮件正文类型，'plain'或'html'，默认为'plain'

**返回值:**
- `bool`: 邮件发送成功返回True，失败返回False

## 测试示例

### 使用 fastmcp dev 测试实例:

```python
fastmcp dev server.py
```

> 这将启动一个开发服务器，允许你在本地测试工具

### 使用FastMCP客户端调用示例:

```python
import asyncio
from fastmcp import Client
from fastmcp.client.transports import (
    SSETransport, 
    PythonStdioTransport, 
    FastMCPTransport
)


async def main():
    async with Client(PythonStdioTransport("/send_mail_mcp/server.py")) as client:
    # async with Client() as client:
        result = await client.call_tool("send_email_with_attachment", {
            "to_emails": ["recipient@example.com"],
            "subject": "测试邮件",
            "body": "<h1>这是一封测试邮件</h1><p>Hello World!</p>",
            # "attachment_paths": ["/path/to/file1.pdf", "/path/to/file2.txt"],
            "body_type": "html"
        })
        print("邮件发送结果:", "成功" if result else "失败")

if __name__ == "__main__":
    asyncio.run(main())
```

## 运行客户端测试

```bash
python client_test.py
```

## 常见问题

1. **认证失败**: 检查邮箱账号和密码是否正确。对于一些邮箱服务商(如Gmail、QQ邮箱等)，可能需要使用应用专用密码而非登录密码。

2. **连接失败**: 检查SMTP服务器地址和端口是否正确，以及是否启用了正确的加密方式。

3. **附件不存在**: 确保附件路径正确且文件存在。

## 环境变量说明

- `SMTP_HOST`: SMTP服务器地址
- `SMTP_PORT`: SMTP服务器端口(常用端口: 25, 465, 587)
- `SMTP_SECURE`: 是否使用SSL加密连接(true/false)
- `SMTP_USER`: SMTP服务器账号
- `SMTP_PASS`: SMTP服务器密码或授权码
- `DEFAULT_FROM_NAME`: 默认发件人名称 暂时无效
- `DEFAULT_FROM_EMAIL`: 默认发件人邮箱地址 暂时无效

## 注意事项

- 请勿在代码中硬编码邮箱凭证，始终使用环境变量
- 确保你有权限使用SMTP服务器发送邮件
- 大量发送邮件可能会被邮件服务商识别为垃圾邮件，请遵循相关政策

## TODO

- [ ] 添加单元测试
- [ ] 日志记录功能

## 贡献

欢迎提交问题和功能请求！如果你有兴趣贡献代码，请遵循以下步骤：
1. Fork 本仓库
2. 创建一个新的分支
3. 提交你的更改
4. 提交Pull Request
5. 确保你的代码遵循PEP 8规范
6. 添加必要的单元测试
7. 更新文档（如果需要）

## License

Apache License 2.0
