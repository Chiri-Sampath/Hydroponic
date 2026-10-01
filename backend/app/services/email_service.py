"""
AgriSmart AI — Email Notification Service
==========================================
Provides email delivery (SMTP / Gmail) for transactional emails such as:
- Password reset instructions
- Account verification
- System alerts

Sender: hydroponiccrop@gmail.com (or configured via MAIL_USERNAME)
"""

import os
import smtplib
import threading
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import current_app

logger = logging.getLogger(__name__)

LAST_EMAIL_STATUS = {
    "attempted_at": None,
    "recipient": None,
    "success": False,
    "message": "No email sent yet since service startup."
}


def _connect_smtp_server(mail_server: str, mail_port: int, use_ssl: bool = False, use_tls: bool = True, timeout: int = 15):
    """
    Connects to SMTP server forcing IPv4 resolution to prevent [Errno 101] Network is unreachable
    on cloud container environments (Render, Heroku) that lack IPv6 routes.
    Tries SSL (port 465) and STARTTLS (port 587) automatically.
    """
    import socket

    # Strategy 1: If connecting to Gmail or port 465, try direct SMTP_SSL first
    attempts = []
    if "gmail.com" in mail_server or mail_port == 465 or use_ssl:
        attempts.append(("smtp.gmail.com", 465, True, False))
        attempts.append(("smtp.gmail.com", 587, False, True))
    else:
        attempts.append((mail_server, mail_port, use_ssl, use_tls))
        attempts.append((mail_server, 465, True, False))
        attempts.append((mail_server, 587, False, True))

    last_error = None
    for host, port, is_ssl, is_tls in attempts:
        try:
            # Resolve IPv4 to bypass unreachable IPv6 routes
            try:
                addr_info = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
                resolved_ip = addr_info[0][4][0] if addr_info else host
            except Exception:
                resolved_ip = host

            if is_ssl:
                server = smtplib.SMTP_SSL(resolved_ip, port, timeout=timeout)
                server.ehlo(host)
                return server
            else:
                server = smtplib.SMTP(resolved_ip, port, timeout=timeout)
                server.ehlo(host)
                if is_tls:
                    server.starttls()
                    server.ehlo(host)
                return server
        except Exception as conn_err:
            last_error = conn_err
            continue

    raise last_error or Exception(f"Could not connect to {mail_server}:{mail_port}")


def test_smtp_connection(app_config: dict = None) -> dict:
    """
    Tests SMTP connectivity and authentication with Gmail without sending an email.
    """
    import datetime
    mail_server = app_config.get("MAIL_SERVER", "smtp.gmail.com") if app_config else os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(app_config.get("MAIL_PORT", 465) if app_config else os.environ.get("MAIL_PORT", 465))
    mail_user = (app_config.get("MAIL_USERNAME", "hydroponiccrop@gmail.com") if app_config else os.environ.get("MAIL_USERNAME", "hydroponiccrop@gmail.com")).strip()
    raw_pass = app_config.get("MAIL_PASSWORD", "") if app_config else os.environ.get("MAIL_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", ""))
    mail_pass = str(raw_pass or "").replace(" ", "").strip()
    use_tls = app_config.get("MAIL_USE_TLS", True) if app_config else True
    use_ssl = app_config.get("MAIL_USE_SSL", True) if app_config else True

    if not mail_pass:
        return {
            "configured": False,
            "smtp_server": mail_server,
            "smtp_user": mail_user,
            "error": "MAIL_PASSWORD is not set in Render Environment Variables. Generate a 16-character Google App Password at myaccount.google.com/apppasswords and add MAIL_PASSWORD to Render."
        }

    try:
        server = _connect_smtp_server(mail_server, mail_port, use_ssl=use_ssl, use_tls=use_tls, timeout=12)
        server.login(mail_user, mail_pass)
        server.quit()
        return {
            "configured": True,
            "authenticated": True,
            "smtp_server": mail_server,
            "smtp_user": mail_user,
            "message": f"Successfully authenticated with {mail_server} as {mail_user}!"
        }
    except Exception as e:
        err_msg = str(e)
        hint = "Ensure you are using a 16-character Google App Password (not your personal Gmail password) and 2-Step Verification is active on hydroponiccrop@gmail.com."
        if "Username and Password not accepted" in err_msg or "BadCredentials" in err_msg or "535" in err_msg:
            hint = "Authentication failed: Please verify that the 16-character Google App Password was copied completely (Google App Passwords have 4 groups of 4 letters, total 16 characters)."
        return {
            "configured": True,
            "authenticated": False,
            "smtp_server": mail_server,
            "smtp_user": mail_user,
            "error": err_msg,
            "hint": hint
        }


def send_email_async(to_email: str, subject: str, html_body: str, text_body: str = None, app_config: dict = None):
    """
    Sends an email via SMTP in a background thread or directly.
    """
    import datetime
    global LAST_EMAIL_STATUS
    mail_server = app_config.get("MAIL_SERVER", "smtp.gmail.com") if app_config else os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    mail_port = int(app_config.get("MAIL_PORT", 465) if app_config else os.environ.get("MAIL_PORT", 465))
    mail_user = (app_config.get("MAIL_USERNAME", "hydroponiccrop@gmail.com") if app_config else os.environ.get("MAIL_USERNAME", "hydroponiccrop@gmail.com")).strip()
    raw_pass = app_config.get("MAIL_PASSWORD", "") if app_config else os.environ.get("MAIL_PASSWORD", os.environ.get("GMAIL_APP_PASSWORD", ""))
    mail_pass = str(raw_pass or "").replace(" ", "").strip()
    mail_sender = app_config.get("MAIL_DEFAULT_SENDER", f"AgriSmart AI <{mail_user}>") if app_config else f"AgriSmart AI <{mail_user}>"
    use_tls = app_config.get("MAIL_USE_TLS", True) if app_config else True
    use_ssl = app_config.get("MAIL_USE_SSL", True) if app_config else True

    LAST_EMAIL_STATUS["attempted_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    LAST_EMAIL_STATUS["recipient"] = to_email

    if not mail_pass:
        msg = f"MAIL_PASSWORD is not set on Render. Email to {to_email} was skipped. Add MAIL_PASSWORD in Render Environment."
        logger.warning(f"[EmailService] {msg}")
        LAST_EMAIL_STATUS["success"] = False
        LAST_EMAIL_STATUS["message"] = msg
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = mail_sender
        msg["To"] = to_email

        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))
        if html_body:
            msg.attach(MIMEText(html_body, "html", "utf-8"))

        server = _connect_smtp_server(mail_server, mail_port, use_ssl=use_ssl, use_tls=use_tls, timeout=15)
        server.login(mail_user, mail_pass)
        server.sendmail(mail_user, [to_email], msg.as_string())
        server.quit()

        logger.info(f"[EmailService] Email successfully sent to {to_email} (Subject: {subject})")
        LAST_EMAIL_STATUS["success"] = True
        LAST_EMAIL_STATUS["message"] = f"Email successfully delivered to {to_email} via {mail_server}!"
        return True
    except Exception as e:
        err_msg = str(e)
        logger.error(f"[EmailService] Failed to send email to {to_email}: {err_msg}")
        LAST_EMAIL_STATUS["success"] = False
        LAST_EMAIL_STATUS["message"] = f"Error sending email: {err_msg}"
        return False


def send_password_reset_email(to_email: str, user_name: str, reset_url: str) -> bool:
    """
    Sends a formatted password reset link email to the user.
    """
    subject = "Reset Your AgriSmart AI Password"
    display_name = user_name or "AgriSmart User"

    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
    .container {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .header {{ background: linear-gradient(135deg, #059669 0%, #0d9488 100%); padding: 28px; text-align: center; color: #ffffff; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
    .header p {{ margin: 6px 0 0 0; font-size: 14px; opacity: 0.9; }}
    .body {{ padding: 32px 28px; }}
    .greeting {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; }}
    .instructions {{ font-size: 14px; line-height: 1.6; color: #475569; margin-bottom: 24px; }}
    .btn-container {{ text-align: center; margin: 30px 0; }}
    .btn {{ display: inline-block; background-color: #059669; color: #ffffff !important; text-decoration: none; padding: 14px 28px; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 2px 4px rgba(5,150,105,0.25); }}
    .note {{ font-size: 13px; color: #64748b; background: #f1f5f9; padding: 12px 16px; border-radius: 6px; border-left: 4px solid #059669; margin-top: 24px; }}
    .fallback {{ font-size: 12px; color: #94a3b8; word-break: break-all; margin-top: 20px; }}
    .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🌱 AgriSmart AI</h1>
      <p>Intelligent Food Production Platform</p>
    </div>
    <div class="body">
      <div class="greeting">Hello {display_name},</div>
      <div class="instructions">
        We received a request to reset the password for your AgriSmart AI account (<strong>{to_email}</strong>). Click the button below to choose a new password:
      </div>
      <div class="btn-container">
        <a href="{reset_url}" class="btn" target="_blank">Reset My Password</a>
      </div>
      <div class="note">
        ⏱️ <strong>Security Notice:</strong> This password reset link is valid for <strong>1 hour</strong>. If you did not request a password reset, you can safely ignore this email — your account remains secure.
      </div>
      <div class="fallback">
        If the button above doesn't work, copy and paste this URL into your web browser:<br>
        <a href="{reset_url}" style="color: #059669;">{reset_url}</a>
      </div>
    </div>
    <div class="footer">
      Sent with ❤️ by AgriSmart AI · From hydroponiccrop@gmail.com<br>
      © 2026 AgriSmart AI. All rights reserved.
    </div>
  </div>
</body>
</html>"""

    text_content = f"""Hello {display_name},

We received a request to reset your AgriSmart AI password.
Please use the following link to reset your password (valid for 1 hour):

{reset_url}

If you did not request this reset, please ignore this message.

— AgriSmart AI Team (hydroponiccrop@gmail.com)
"""

    app_config = None
    try:
        app_config = {
            "MAIL_SERVER": current_app.config.get("MAIL_SERVER"),
            "MAIL_PORT": current_app.config.get("MAIL_PORT"),
            "MAIL_USERNAME": current_app.config.get("MAIL_USERNAME"),
            "MAIL_PASSWORD": current_app.config.get("MAIL_PASSWORD"),
            "MAIL_DEFAULT_SENDER": current_app.config.get("MAIL_DEFAULT_SENDER"),
            "MAIL_USE_TLS": current_app.config.get("MAIL_USE_TLS"),
            "MAIL_USE_SSL": current_app.config.get("MAIL_USE_SSL"),
        }
    except Exception:
        pass

    # Launch in a daemon thread so user receives instant API response
    thread = threading.Thread(
        target=send_email_async,
        args=(to_email, subject, html_content, text_content, app_config),
        daemon=True,
    )
    thread.start()
    return True
