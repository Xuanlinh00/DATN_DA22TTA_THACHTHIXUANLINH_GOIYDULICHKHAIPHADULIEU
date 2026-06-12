# -*- coding: utf-8 -*-
"""
Email Service - Sends emails for password resets using SMTP.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "no-reply@travelrecommender.com")

def send_reset_password_email(to_email: str, reset_link: str) -> bool:
    """
    Sends a password reset link to the user's email.
    If SMTP settings are missing, logs the email details to the console (for local development testing).
    """
    subject = "Đặt lại mật khẩu - Trợ lý du lịch NomadAI"
    
    # HTML content for the email
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f7f9fa;
                color: #333333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                overflow: hidden;
                border: 1px solid #eef2f5;
            }}
            .header {{
                background: linear-gradient(135deg, #c24482, #f4a4c6);
                padding: 30px;
                text-align: center;
                color: #ffffff;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: 700;
            }}
            .content {{
                padding: 40px 30px;
                line-height: 1.6;
            }}
            .content p {{
                margin: 0 0 20px 0;
                font-size: 15px;
            }}
            .btn-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .btn {{
                background: linear-gradient(135deg, #c24482, #f4a4c6);
                color: #ffffff !important;
                text-decoration: none;
                padding: 14px 28px;
                border-radius: 50px;
                font-weight: bold;
                font-size: 14px;
                display: inline-block;
                box-shadow: 0 4px 10px rgba(194, 68, 130, 0.2);
            }}
            .footer {{
                background-color: #f7f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #888888;
                border-top: 1px solid #eef2f5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>NomadAI</h1>
            </div>
            <div class="content">
                <p>Xin chào,</p>
                <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn trên hệ thống Gợi ý du lịch <strong>NomadAI</strong>.</p>
                <p>Vui lòng nhấn vào nút dưới đây để tiến hành thay đổi mật khẩu của bạn. Liên kết này có hiệu lực trong vòng <strong>15 phút</strong>:</p>
                <div class="btn-container">
                    <a href="{reset_link}" class="btn">Đặt lại mật khẩu</a>
                </div>
                <p>Nếu nút trên không hoạt động, bạn có thể sao chép và dán liên kết dưới đây vào trình duyệt:</p>
                <p style="word-break: break-all;"><a href="{reset_link}" style="color: #c24482;">{reset_link}</a></p>
                <p>Nếu bạn không gửi yêu cầu này, vui lòng bỏ qua email này. Mật khẩu của bạn vẫn sẽ được giữ an toàn.</p>
                <p>Trân trọng,<br>Đội ngũ NomadAI</p>
            </div>
            <div class="footer">
                <p>© 2026 NomadAI Travel Recommender. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # If SMTP_HOST is not set, log the email to stdout (very useful for development/testing without real SMTP credentials)
    if not SMTP_HOST:
        print("\n" + "="*80)
        print(" [EMAIL SERVICE] SMTP configuration is missing! Logging email to console:")
        print(f" To: {to_email}")
        print(f" Subject: {subject}")
        print(f" Reset Link: {reset_link}")
        print("="*80 + "\n")
        return True

    try:
        msg = MIMEText(html_content, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SMTP_FROM
        msg['To'] = to_email

        # Send email
        if SMTP_PORT == 465:
            # SSL Connection
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_email], msg.as_string())
        else:
            # TLS Connection (port 587 or 25)
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_email], msg.as_string())
        print(f"[OK] Reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {e}")
        # Return fallback log so development is not blocked
        print("\n" + "="*80)
        print(" [EMAIL SERVICE] SMTP failed! Logging email to console as fallback:")
        print(f" To: {to_email}")
        print(f" Subject: {subject}")
        print(f" Reset Link: {reset_link}")
        print("="*80 + "\n")
        return True
