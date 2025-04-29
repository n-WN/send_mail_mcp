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