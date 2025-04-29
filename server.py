import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr
import mimetypes
from typing import List, Optional, Literal # 导入类型提示

from fastmcp import FastMCP

# --- 环境变量加载 ---
# 尝试加载 .env 文件中的环境变量（如果使用了 python-dotenv）
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("环境变量从 .env 文件加载成功。")
except ImportError:
    print("未安装 python-dotenv，将从系统环境变量中读取配置。")
except Exception as e:
    print(f"加载 .env 文件出错: {e}")

# --- FastMCP 实例化 ---
# 你可以在这里根据需要添加一些描述
mcp = FastMCP("Mail Tool Server 📧")

# --- 邮件发送函数（与之前相同，可以作为内部函数或单独定义） ---
# 我们保持原函数不变，以便工具函数调用它
def _send_email_core(
    to_email_list, # 内部使用列表
    subject,
    body,
    attachment_paths=None,
    body_type='plain' # 'plain' or 'html'
):
    """
    核心邮件发送逻辑，从环境变量读取配置。
    注意：这个是内部使用的函数，不直接暴露为mcp工具。
    """
    # 从环境变量获取配置
    smtp_host = os.getenv("SMTP_HOST")
    # 尝试使用 465 端口作为默认值，因为QQ邮箱常使用 465 + SSL
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    # 对于465端口，默认应该是 True
    smtp_secure_env = os.getenv("SMTP_SECURE")
    if smtp_secure_env is None:
         # 如果环境变量没设置 SMTP_SECURE，根据端口推断一个常用默认值
        smtp_secure = (smtp_port == 465) # 465通常是SSL，587通常是STARTTLS
    else:
        smtp_secure = smtp_secure_env.lower() == "true"


    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS") # 通常是授权码
    from_name = os.getenv("DEFAULT_FROM_NAME", "Sender")
    from_email = os.getenv("DEFAULT_FROM_EMAIL", smtp_user)

    # 检查必要配置是否存在
    if not all([smtp_host, smtp_user, smtp_pass]):
        print("错误：SMTP_HOST, SMTP_USER, SMTP_PASS 环境变量未设置。")
        return False

    # 创建邮件对象
    msg = MIMEMultipart()
    # 修复formataddr参数类型不兼容问题，确保from_name和from_email非空
    from_name = from_name or "Sender"  # 如果为None则使用默认值
    from_email = from_email or ""  # 如果为None则使用空字符串
    msg['From'] = formataddr((from_name, from_email))

    # 处理收件人列表（这个内部函数现在期望一个列表）
    if not isinstance(to_email_list, list) or not to_email_list:
         print("错误：收件人邮箱列表不能为空。")
         return False

    recipients = to_email_list
    msg['To'] = ", ".join(recipients) # To头部是逗号分隔的字符串

    msg['Subject'] = subject
    msg.attach(MIMEText(body, body_type, 'utf-8'))

    # 添加附件
    if attachment_paths:
        if not isinstance(attachment_paths, list):
            print("警告：attachment_paths 应该是一个列表。")
            attachment_paths = [attachment_paths] # 如果传入的不是列表，尝试转为列表

        for attachment_path in attachment_paths:
            if not isinstance(attachment_path, str):
                 print(f"警告：附件路径 '{attachment_path}' 不是有效的字符串路径，跳过。")
                 continue
            try:
                if not os.path.exists(attachment_path):
                    print(f"警告：附件文件未找到 - {attachment_path}")
                    continue

                filename = os.path.basename(attachment_path)
                ctype, encoding = mimetypes.guess_type(attachment_path)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'

                maintype, subtype = ctype.split('/', 1)
                part = MIMEBase(maintype, subtype)

                with open(attachment_path, 'rb') as file:
                    part.set_payload(file.read())

                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(part)

            except Exception as e:
                print(f"警告：处理附件 {attachment_path} 时出错 - {e}")
                continue

    # 连接到SMTP服务器并发送邮件
    server = None
    try:
        # 确保smtp_host不为None
        smtp_host_str = str(smtp_host) if smtp_host is not None else ""
        
        if smtp_secure:
            print(f"连接到 SMTP 服务器: {smtp_host_str}:{smtp_port} 使用 SSL...")
            server = smtplib.SMTP_SSL(smtp_host_str, smtp_port, timeout=10)
        else:
            print(f"连接到 SMTP 服务器: {smtp_host_str}:{smtp_port}...")
            server = smtplib.SMTP(smtp_host_str, smtp_port, timeout=10)
            # 尝试启动 TLS 加密，这对于端口 587 是标准的
            # 检查服务器是否支持 STARTTLS
            if server.has_extn('STARTTLS'):
                 print("启动 STARTTLS...")
                 server.starttls()
            else:
                 print("警告：服务器不支持 STARTTLS 或配置为非安全连接（端口587应尝试STARTTLS）。")


        print("登录到 SMTP 服务器...")
        # 确保smtp_user和smtp_pass不为None
        smtp_user_str = str(smtp_user) if smtp_user is not None else ""
        smtp_pass_str = str(smtp_pass) if smtp_pass is not None else ""
        server.login(smtp_user_str, smtp_pass_str)

        print(f"发送邮件到: {recipients}...")
        # 确保from_email不为None
        from_email_str = str(from_email) if from_email is not None else ""
        server.sendmail(from_email_str, recipients, msg.as_string())

        print("邮件发送成功！")
        return True

    except smtplib.SMTPAuthenticationError:
         print("错误：SMTP认证失败。请检查用户名和授权码（或密码）。")
         return False
    except smtplib.SMTPConnectError as e:
         print(f"错误：SMTP连接失败 - {e}")
         print("请检查SMTP_HOST, SMTP_PORT, SMTP_SECURE配置以及网络防火墙。")
         return False
    except smtplib.SMTPException as e:
        print(f"错误：发送邮件失败 - {e}")
        return False
    except Exception as e:
        print(f"发生意外错误：{e}")
        return False
    finally:
        if server:
            try:
                 server.quit()
                 print("SMTP 连接已关闭。")
            except Exception as e:
                 print(f"关闭SMTP连接时发生错误: {e}")


# --- FastMCP Tool 函数 ---
# 这是一个封装函数，用于适配FastMCP的输入/输出，并调用核心发送逻辑
@mcp.tool()
def send_email_with_attachment(
    to_emails: List[str],
    subject: str,
    body: str,
    attachment_paths: Optional[List[str]] = None,
    body_type: Literal['plain', 'html'] = 'plain'
) -> bool:
    """
    发送带有附件的邮件。

    Args:
        to_emails (List[str]): 收件人邮箱地址列表。
        subject (str): 邮件主题。
        body (str): 邮件正文。
        attachment_paths (Optional[List[str]]): 附件文件路径列表。默认为 None。
        body_type (Literal['plain', 'html']): 邮件正文类型，'plain' 或 'html'。默认为 'plain'。

    Returns:
        bool: 邮件发送成功返回 True，失败返回 False。
    """
    print(f"收到发送邮件请求：主题='{subject}', 收件人={to_emails}")
    # 调用内部核心发送逻辑
    success = _send_email_core(to_emails, subject, body, attachment_paths, body_type)

    if success:
        print("邮件工具执行成功。")
    else:
        print("邮件工具执行失败。")

    return success


# --- FastMCP Server 运行 ---
if __name__ == "__main__":
    # 确保在运行服务器之前，你的 .env 文件已配置好或环境变量已设置
    print("FastMCP Mail Tool Server 正在启动...")
    # 为了测试，可以先手动创建一些测试文件
    test_attachment_file1 = "test_attachment_1.txt"
    if not os.path.exists(test_attachment_file1):
        with open(test_attachment_file1, "w", encoding='utf-8') as f:
            f.write("这是一个测试文本文件（UTF-8）。\nThis is a test text file (UTF-8).")
        print(f"创建测试文件: {test_attachment_file1}")
    # test_attachment_file2 = "test_attachment_2.pdf" # 如果需要测试PDF，请确保此文件存在

    mcp.run()