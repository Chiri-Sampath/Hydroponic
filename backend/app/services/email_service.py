"""
AgriSmart AI — Email Notification Service
==========================================
Uses Brevo (formerly Sendinblue) HTTP REST API over port 443.
Render Free Tier blocks all SMTP ports; this approach is not affected.

Required environment variable (set in Render Dashboard → Environment):
  BREVO_API_KEY   — your Brevo API key (free at https://www.brevo.com)

Optional:
  MAIL_FROM_EMAIL  — verified sender email (default: agrismart@agrismart-mail.com)
  MAIL_FROM_NAME   — display name (default: AgriSmart AI)

IMPORTANT: The sender email MUST be verified in your Brevo account under
"Senders & Domains". By default we use an address that works without
domain verification on Brevo free tier.
"""

import os
import logging
import datetime

import requests

logger = logging.getLogger(__name__)

LAST_EMAIL_STATUS = {
    "attempted_at": None,
    "recipient": None,
    "provider": None,
    "success": False,
    "message": "No email sent yet since service startup.",
    "error_detail": None,
}


def _get_cfg(key: str, default: str = "") -> str:
    """Read from Flask app config first, then environment variables."""
    try:
        from flask import current_app
        val = current_app.config.get(key)
        if val:
            return str(val).strip()
    except Exception:
        pass
    return str(os.environ.get(key, default) or "").strip()


def _send_via_brevo(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    """
    Send via Brevo (Sendinblue) REST API.
    Sender must be verified at: https://app.brevo.com/senders
    """
    api_key = _get_cfg("BREVO_API_KEY")
    if not api_key:
        return {"ok": False, "error": "BREVO_API_KEY not configured"}

    # Use the configured sender — MUST be verified in Brevo Senders list
    from_email = _get_cfg("MAIL_FROM_EMAIL", "noreply@agrismart.ai")
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

    try:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers,
            timeout=20,
        )
        if resp.status_code in (200, 201):
            return {"ok": True, "provider": "brevo", "response": resp.json()}
        # Capture full error body for diagnostics
        return {
            "ok": False,
            "provider": "brevo",
            "error": f"HTTP {resp.status_code}",
            "detail": resp.text[:500],
        }
    except Exception as exc:
        return {"ok": False, "provider": "brevo", "error": str(exc)}


def _dispatch_email(to_email: str, to_name: str, subject: str, html_body: str, text_body: str) -> dict:
    """
    Sends the email synchronously (no thread) so errors are immediately
    captured in LAST_EMAIL_STATUS and visible on /api/email-status.
    """
    global LAST_EMAIL_STATUS

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    LAST_EMAIL_STATUS["attempted_at"] = now
    LAST_EMAIL_STATUS["recipient"] = to_email
    LAST_EMAIL_STATUS["error_detail"] = None

    # Try Brevo first
    result = _send_via_brevo(to_email, to_name, subject, html_body, text_body)
    if result.get("ok"):
        logger.info(f"[EmailService] ✓ Email sent to {to_email} via brevo")
        LAST_EMAIL_STATUS["success"] = True
        LAST_EMAIL_STATUS["provider"] = "brevo"
        LAST_EMAIL_STATUS["message"] = f"Delivered to {to_email} via Brevo"
        LAST_EMAIL_STATUS["error_detail"] = None
        return result

    # Brevo failed — capture error
    err_msg = result.get("error", "Unknown error")
    err_detail = result.get("detail", "")
    logger.error(f"[EmailService] ✗ Brevo failed for {to_email}: {err_msg} | {err_detail}")
    LAST_EMAIL_STATUS["success"] = False
    LAST_EMAIL_STATUS["provider"] = "brevo"
    LAST_EMAIL_STATUS["message"] = f"Failed: {err_msg}"
    LAST_EMAIL_STATUS["error_detail"] = err_detail or err_msg

    return {"ok": False, "error": err_msg, "detail": err_detail}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def test_smtp_connection(app_config: dict = None) -> dict:
    """
    For the /api/email-status endpoint.
    Returns provider configuration status.
    """
    api_key = _get_cfg("BREVO_API_KEY")
    from_email = _get_cfg("MAIL_FROM_EMAIL", "noreply@agrismart.ai")

    if not api_key:
        return {
            "configured": False,
            "authenticated": False,
            "method": "HTTP API (SMTP blocked on Render free tier)",
            "error": "BREVO_API_KEY not set",
            "fix": (
                "1. Sign up free at https://www.brevo.com (no credit card).\n"
                "2. SMTP & API → API Keys → Create key.\n"
                "3. Render Dashboard → agrismart-backend → Environment → add BREVO_API_KEY.\n"
                "4. Also add: MAIL_FROM_EMAIL = <a verified sender from Brevo Senders list>"
            ),
        }

    return {
        "configured": True,
        "authenticated": True,
        "method": "HTTP API",
        "providers": ["Brevo"],
        "sender": from_email,
        "message": f"Ready to send emails via Brevo from {from_email}",
        "warning": (
            None if from_email != "hydroponiccrop@gmail.com"
            else "Gmail addresses as sender require domain verification in Brevo. "
                 "Add a verified sender at https://app.brevo.com/senders or set "
                 "MAIL_FROM_EMAIL to a Brevo-verified address."
        ),
    }


def send_password_reset_email(to_email: str, user_name: str, reset_url: str) -> bool:
    """Send a branded password reset email via Brevo HTTP API."""
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
    <div class="ft">© 2026 AgriSmart AI. All rights reserved.</div>
  </div>
</body></html>"""

    text_body = f"""Hello {display_name},

Reset your AgriSmart AI password using this link (valid 1 hour):
{reset_url}

If you didn't request this, ignore this email.

— AgriSmart AI Team
"""

    result = _dispatch_email(to_email, display_name, subject, html_body, text_body)
    return result.get("ok", False)
