"""
AgriSmart AI — Email Notification Service
==========================================
Uses HTTP REST API (port 443) instead of SMTP (blocked on Render free tier).

Supported providers (auto-selected by env vars):
  1. Brevo (formerly Sendinblue) — free 300 emails/day, no credit card
     Set: BREVO_API_KEY
  2. SendGrid — free 100 emails/day
     Set: SENDGRID_API_KEY
  3. Mailgun — first 100 emails/month free
     Set: MAILGUN_API_KEY + MAILGUN_DOMAIN

Sender: hydroponiccrop@gmail.com (configured via MAIL_FROM_EMAIL)
"""

import os
import threading
import logging

import requests

logger = logging.getLogger(__name__)

LAST_EMAIL_STATUS = {
    "attempted_at": None,
    "recipient": None,
    "provider": None,
    "success": False,
    "message": "No email sent yet since service startup.",
}


def _get_cfg(key: str, default: str = "") -> str:
    """Read from Flask app config first, then from env vars."""
    try:
        from flask import current_app
        val = current_app.config.get(key)
        if val:
            return str(val).strip()
    except Exception:
        pass
    return str(os.environ.get(key, default) or "").strip()


# ---------------------------------------------------------------------------
# Provider: Brevo (formerly Sendinblue)  — free 300/day, HTTP API
# ---------------------------------------------------------------------------
def _send_via_brevo(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    api_key = _get_cfg("BREVO_API_KEY")
    if not api_key:
        return {"ok": False, "error": "BREVO_API_KEY not set"}

    from_email = _get_cfg("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com")
    from_name = _get_cfg("MAIL_FROM_NAME", "AgriSmart AI")

    payload = {
        "sender": {"name": from_name, "email": from_email},
        "to": [{"email": to_email, "name": to_name or to_email}],
        "subject": subject,
        "htmlContent": html_body,
        "textContent": text_body or "",
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key,
    }
    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers=headers,
        timeout=20,
    )
    if resp.status_code in (200, 201):
        return {"ok": True, "provider": "brevo", "response": resp.json()}
    return {"ok": False, "provider": "brevo", "error": f"HTTP {resp.status_code}: {resp.text}"}


# ---------------------------------------------------------------------------
# Provider: SendGrid  — free 100/day, HTTP API
# ---------------------------------------------------------------------------
def _send_via_sendgrid(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    api_key = _get_cfg("SENDGRID_API_KEY")
    if not api_key:
        return {"ok": False, "error": "SENDGRID_API_KEY not set"}

    from_email = _get_cfg("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com")
    from_name = _get_cfg("MAIL_FROM_NAME", "AgriSmart AI")

    payload = {
        "personalizations": [{"to": [{"email": to_email, "name": to_name or to_email}], "subject": subject}],
        "from": {"email": from_email, "name": from_name},
        "content": [
            {"type": "text/plain", "value": text_body or subject},
            {"type": "text/html", "value": html_body},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        json=payload,
        headers=headers,
        timeout=20,
    )
    if resp.status_code in (200, 202):
        return {"ok": True, "provider": "sendgrid"}
    return {"ok": False, "provider": "sendgrid", "error": f"HTTP {resp.status_code}: {resp.text}"}


# ---------------------------------------------------------------------------
# Provider: Mailgun  — 100/month free on US region, HTTP API
# ---------------------------------------------------------------------------
def _send_via_mailgun(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    api_key = _get_cfg("MAILGUN_API_KEY")
    domain = _get_cfg("MAILGUN_DOMAIN")
    if not api_key or not domain:
        return {"ok": False, "error": "MAILGUN_API_KEY or MAILGUN_DOMAIN not set"}

    from_email = _get_cfg("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com")
    from_name = _get_cfg("MAIL_FROM_NAME", "AgriSmart AI")
    region = _get_cfg("MAILGUN_REGION", "us")  # "us" or "eu"
    base = "https://api.eu.mailgun.net" if region == "eu" else "https://api.mailgun.net"

    resp = requests.post(
        f"{base}/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"{from_name} <{from_email}>",
            "to": [f"{to_name or ''} <{to_email}>"],
            "subject": subject,
            "text": text_body or "",
            "html": html_body,
        },
        timeout=20,
    )
    if resp.status_code in (200, 201):
        return {"ok": True, "provider": "mailgun"}
    return {"ok": False, "provider": "mailgun", "error": f"HTTP {resp.status_code}: {resp.text}"}


# ---------------------------------------------------------------------------
# Dispatcher — tries providers in order
# ---------------------------------------------------------------------------
PROVIDERS = [
    ("brevo", _send_via_brevo),
    ("sendgrid", _send_via_sendgrid),
    ("mailgun", _send_via_mailgun),
]


def _dispatch_email(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    """
    Tries each configured email provider in order and returns on first success.
    All requests go over HTTPS port 443 — no SMTP firewall issues.
    """
    import datetime
    global LAST_EMAIL_STATUS

    LAST_EMAIL_STATUS["attempted_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    LAST_EMAIL_STATUS["recipient"] = to_email

    configured_providers = []
    if _get_cfg("BREVO_API_KEY"):
        configured_providers.append(("brevo", _send_via_brevo))
    if _get_cfg("SENDGRID_API_KEY"):
        configured_providers.append(("sendgrid", _send_via_sendgrid))
    if _get_cfg("MAILGUN_API_KEY") and _get_cfg("MAILGUN_DOMAIN"):
        configured_providers.append(("mailgun", _send_via_mailgun))

    if not configured_providers:
        msg = (
            "No email API key configured. "
            "Set BREVO_API_KEY in Render Environment Variables. "
            "Get a free key at https://www.brevo.com (300 emails/day, no credit card)."
        )
        logger.warning(f"[EmailService] {msg}")
        LAST_EMAIL_STATUS["success"] = False
        LAST_EMAIL_STATUS["message"] = msg
        return {"ok": False, "error": msg}

    for name, fn in configured_providers:
        try:
            result = fn(to_email, to_name, subject, html_body, text_body)
            if result.get("ok"):
                logger.info(f"[EmailService] Email sent to {to_email} via {name}")
                LAST_EMAIL_STATUS["success"] = True
                LAST_EMAIL_STATUS["provider"] = name
                LAST_EMAIL_STATUS["message"] = f"Delivered via {name}"
                return result
            else:
                logger.warning(f"[EmailService] {name} failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"[EmailService] Exception using {name}: {e}")

    msg = "All configured email providers failed."
    LAST_EMAIL_STATUS["success"] = False
    LAST_EMAIL_STATUS["message"] = msg
    return {"ok": False, "error": msg}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def test_smtp_connection(app_config: dict = None) -> dict:
    """
    For the /api/email-status endpoint — tests if any HTTP email provider is configured.
    (Named test_smtp_connection for backward compatibility.)
    """
    brevo = _get_cfg("BREVO_API_KEY")
    sendgrid = _get_cfg("SENDGRID_API_KEY")
    mailgun_key = _get_cfg("MAILGUN_API_KEY")
    mailgun_domain = _get_cfg("MAILGUN_DOMAIN")

    providers_ready = []
    if brevo:
        providers_ready.append("Brevo")
    if sendgrid:
        providers_ready.append("SendGrid")
    if mailgun_key and mailgun_domain:
        providers_ready.append("Mailgun")

    if not providers_ready:
        return {
            "configured": False,
            "authenticated": False,
            "method": "HTTP API (SMTP is blocked on Render free tier)",
            "error": "No email API key found.",
            "fix": (
                "1. Go to https://www.brevo.com → sign up free (no credit card).\n"
                "2. Go to SMTP & API → API Keys → Create a new API key.\n"
                "3. In Render Dashboard → agrismart-backend → Environment,\n"
                "   add: BREVO_API_KEY = <your key>  and  MAIL_FROM_EMAIL = hydroponiccrop@gmail.com\n"
                "4. Click Save Changes on Render."
            ),
        }

    return {
        "configured": True,
        "authenticated": True,
        "method": "HTTP API",
        "providers": providers_ready,
        "sender": _get_cfg("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com"),
        "message": f"Ready to send emails via: {', '.join(providers_ready)}",
    }


def send_password_reset_email(to_email: str, user_name: str, reset_url: str) -> bool:
    """Sends a branded password reset email using the configured HTTP email provider."""
    subject = "Reset Your AgriSmart AI Password"
    display_name = user_name or "AgriSmart User"

    html_body = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f8fafc;margin:0;padding:20px;color:#1e293b}}
  .c{{max-width:560px;margin:0 auto;background:#fff;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden}}
  .h{{background:linear-gradient(135deg,#059669,#0d9488);padding:28px;text-align:center;color:#fff}}
  .h h1{{margin:0;font-size:24px;font-weight:700}}.h p{{margin:6px 0 0;font-size:14px;opacity:.9}}
  .b{{padding:32px 28px}}.g{{font-size:16px;font-weight:600;margin-bottom:16px}}
  .i{{font-size:14px;line-height:1.6;color:#475569;margin-bottom:24px}}
  .bc{{text-align:center;margin:30px 0}}
  .btn{{display:inline-block;background:#059669;color:#fff!important;text-decoration:none;padding:14px 28px;border-radius:8px;font-weight:600;font-size:15px}}
  .n{{font-size:13px;color:#64748b;background:#f1f5f9;padding:12px 16px;border-radius:6px;border-left:4px solid #059669;margin-top:24px}}
  .f{{font-size:12px;color:#94a3b8;word-break:break-all;margin-top:20px}}
  .ft{{background:#f8fafc;padding:20px;text-align:center;font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0}}
</style></head>
<body>
  <div class="c">
    <div class="h"><h1>🌱 AgriSmart AI</h1><p>Intelligent Food Production Platform</p></div>
    <div class="b">
      <div class="g">Hello {display_name},</div>
      <div class="i">We received a request to reset the password for your AgriSmart AI account (<strong>{to_email}</strong>). Click the button below to set a new password:</div>
      <div class="bc"><a href="{reset_url}" class="btn" target="_blank">Reset My Password</a></div>
      <div class="n">⏱️ <strong>This link is valid for 1 hour.</strong> If you did not request a reset, ignore this email — your account is safe.</div>
      <div class="f">If the button doesn't work, copy this URL:<br><a href="{reset_url}" style="color:#059669">{reset_url}</a></div>
    </div>
    <div class="ft">Sent by AgriSmart AI · hydroponiccrop@gmail.com<br>© 2026 AgriSmart AI. All rights reserved.</div>
  </div>
</body></html>"""

    text_body = f"""Hello {display_name},

Reset your AgriSmart AI password using this link (valid 1 hour):
{reset_url}

If you didn't request this, ignore this email.

— AgriSmart AI Team
"""

    # Fire and forget in background thread
    thread = threading.Thread(
        target=_dispatch_email,
        args=(to_email, display_name, subject, html_body, text_body),
        daemon=True,
    )
    thread.start()
    return True
