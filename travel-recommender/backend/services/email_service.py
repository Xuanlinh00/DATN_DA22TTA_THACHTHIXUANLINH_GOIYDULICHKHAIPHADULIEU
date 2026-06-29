# -*- coding: utf-8 -*-
"""
Email Service - Sends emails for password resets.
Reads EMAIL_SERVICE / EMAIL_USER / EMAIL_PASS from .env
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from pathlib import Path
from dotenv import load_dotenv

# Load .env tu thu muc goc du an (2 cap tren services/)
_root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_root_env, override=True)

EMAIL_SERVICE = os.getenv("EMAIL_SERVICE", "gmail").strip().lower()
EMAIL_USER    = os.getenv("EMAIL_USER", "").strip()
EMAIL_PASS    = os.getenv("EMAIL_PASS", "").strip()
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Tro ly du lich Nâu").strip()
FRONTEND_URL  = os.getenv("FRONTEND_URL", "http://127.0.0.1:3000").strip()

# Map service name -> SMTP host/port
_SERVICE_MAP = {
    "gmail":   ("smtp.gmail.com",        587),
    "outlook": ("smtp.office365.com",    587),
    "hotmail": ("smtp.office365.com",    587),
    "yahoo":   ("smtp.mail.yahoo.com",   587),
}

_PLACEHOLDER = "your_email@gmail.com"


def _get_smtp_host_port():
    """Tra ve (host, port) tuong ung voi EMAIL_SERVICE."""
    return _SERVICE_MAP.get(EMAIL_SERVICE, ("smtp.gmail.com", 587))


def _is_configured() -> bool:
    """Kiem tra da cau hinh email day du chua."""
    return (
        bool(EMAIL_USER)
        and bool(EMAIL_PASS)
        and EMAIL_USER != _PLACEHOLDER
        and "@" in EMAIL_USER
    )


def _log_fallback(to_email: str, subject: str, reset_link: str, reason: str = ""):
    """In thong tin email ra console (dung khi SMTP chua cau hinh hoac loi)."""
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"  [EMAIL] {reason or 'SMTP chua cau hinh'} - In ra console:")
    print(f"  To      : {to_email}")
    print(f"  Subject : {subject}")
    print(f"  Link    : {reset_link}")
    print(f"{sep}\n")


def _build_html(reset_link: str) -> str:
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f7f9fa;
                color: #333333;
                margin: 0; padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background: #ffffff;
                border-radius: 16px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);
                overflow: hidden;
                border: 1px solid #eef2f5;
            }}
            .header {{
                background: linear-gradient(135deg, #c24482, #f4a4c6);
                padding: 32px 30px;
                text-align: center;
                color: #fff;
            }}
            .header h1 {{ margin: 0; font-size: 26px; font-weight: 700; letter-spacing: 0.5px; }}
            .header p  {{ margin: 6px 0 0; font-size: 13px; opacity: .85; }}
            .content {{ padding: 40px 32px; line-height: 1.7; }}
            .content p {{ margin: 0 0 18px; font-size: 15px; color: #444; }}
            .btn-wrap {{ text-align: center; margin: 32px 0; }}
            .btn {{
                background: linear-gradient(135deg, #c24482, #f4a4c6);
                color: #fff !important;
                text-decoration: none;
                padding: 14px 32px;
                border-radius: 50px;
                font-weight: 700;
                font-size: 15px;
                display: inline-block;
                box-shadow: 0 4px 14px rgba(194,68,130,0.3);
                letter-spacing: 0.3px;
            }}
            .divider {{ border: none; border-top: 1px solid #eef2f5; margin: 24px 0; }}
            .link-box {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 12px;
                color: #6c757d;
                word-break: break-all;
            }}
            .link-box a {{ color: #c24482; }}
            .expire-note {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #fff8f0;
                border: 1px solid #fde8c8;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #b45309;
                margin-bottom: 20px;
            }}
            .footer {{
                background: #f7f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #9ca3af;
                border-top: 1px solid #eef2f5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✈️ Nâu</h1>
                <p>Hệ thống gợi ý du lịch thông minh</p>
            </div>
            <div class="content">
                <p>Xin chào,</p>
                <p>Chúng tôi nhận được yêu cầu <strong>đặt lại mật khẩu</strong> cho tài khoản của bạn tại Nâu.</p>
                <div class="expire-note">
                    ⏳ Liên kết đặt lại mật khẩu này sẽ hết hạn sau <strong>10 phút</strong>.
                </div>
                <div class="btn-wrap">
                    <a href="{reset_link}" class="btn">Đặt lại mật khẩu</a>
                </div>
                <hr class="divider">
                <p style="font-size:13px; color:#6b7280;">
                    Nếu nút bấm trên không hoạt động, vui lòng sao chép và dán liên kết dưới đây vào trình duyệt của bạn:
                </p>
                <div class="link-box">
                    <a href="{reset_link}">{reset_link}</a>
                </div>
                <hr class="divider">
                <p style="font-size:13px; color:#9ca3af;">
                    Nếu bạn không gửi yêu cầu đặt lại mật khẩu này, bạn có thể bỏ qua thư này một cách an toàn. 
                    Mật khẩu của bạn vẫn được bảo mật.
                </p>
                <p style="color:#6b7280;">Trân trọng,<br><strong>Đội ngũ Nâu</strong></p>
            </div>
            <div class="footer">
                <p>&copy; 2026 Nâu Travel Recommender. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


def send_reset_password_email(to_email: str, reset_link: str) -> bool:
    """
    Gửi email đặt lại mật khẩu.
    Đọc EMAIL_SERVICE / EMAIL_USER / EMAIL_PASS từ .env.
    Nếu chưa cấu hình -> in ra console.
    """
    subject = "Đặt lại mật khẩu - Trợ lý du lịch Nâu"

    if not _is_configured():
        _log_fallback(to_email, subject, reset_link,
                      "EMAIL chưa được cấu hình trong .env")
        return True

    smtp_host, smtp_port = _get_smtp_host_port()

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, "utf-8").encode()
        msg["From"]    = f"{Header(EMAIL_FROM_NAME, 'utf-8').encode()} <{EMAIL_USER}>"
        msg["To"]      = to_email

        text_part = MIMEText(
            f"Đặt lại mật khẩu Nâu\n\nLiên kết: {reset_link}\n\n(Hết hạn sau 10 phút)",
            "plain", "utf-8"
        )
        html_part = MIMEText(_build_html(reset_link), "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)

        # STARTTLS (port 587) - chuẩn cho Gmail/Outlook
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, [to_email], msg.as_bytes())

        print(f"[EMAIL] OK - Da gui email reset toi {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL] Xac thuc that bai: {e}")
        print("  -> Kiem tra EMAIL_USER, EMAIL_PASS trong .env")
        print("  -> Gmail: phai dung App Password (16 ky tu)")
        _log_fallback(to_email, subject, reset_link, "SMTPAuthenticationError")
        return True  # Không ném lỗi lên client - chỉ log

    except Exception as e:
        print(f"[EMAIL] Loi gui email: {e}")
        _log_fallback(to_email, subject, reset_link, f"Loi: {e}")
        return True
