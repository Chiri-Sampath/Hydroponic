"""
AgriSmart AI — Health Check Route
===================================
Returns API health status, database connectivity, and email diagnostics.
Public endpoints — no authentication required.
"""

from flask import Blueprint, jsonify, current_app

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    GET /api/health
    ---------------
    Returns service health, database status, and version.
    """
    db_status = "connected"
    products_count = 0
    try:
        from ..models.cultivation import Product
        products_count = Product.query.count()
    except Exception as e:
        db_status = f"error: {e}"

    return jsonify(
        {
            "status": "ok",
            "service": current_app.config.get("APP_NAME", "AgriSmart AI"),
            "version": current_app.config.get("APP_VERSION", "1.0.0"),
            "build": "2026.10.02-v5-brevo",
            "database": db_status,
            "products_count": products_count,
        }
    ), 200


@health_bp.route("/init", methods=["GET", "POST"])
def init_database():
    """
    GET/POST /api/init
    ------------------
    Initialize all tables and seed master data on demand.
    """
    try:
        from ..extensions import db
        from .. import models
        db.create_all()
        from ..services.seeder import seed_all_master_data
        seed_all_master_data(db.session)
        from ..models.cultivation import Product
        count = Product.query.count()
        return jsonify({
            "success": True,
            "build": "2026.10.02-v5-brevo",
            "message": "Database initialized and master data seeded successfully",
            "products_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "build": "2026.10.02-v5-brevo",
            "error": str(e)
        }), 500


@health_bp.route("/email-status", methods=["GET"])
def email_status():
    """
    GET /api/email-status
    ---------------------
    Diagnostics: shows which HTTP email provider is active and last send attempt.
    """
    try:
        from ..services.email_service import test_smtp_connection, LAST_EMAIL_STATUS
        provider_report = test_smtp_connection()
        return jsonify({
            "provider_test": provider_report,
            "last_email_attempt": LAST_EMAIL_STATUS
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@health_bp.route("/send-reset-email", methods=["POST"])
def send_reset_email():
    """
    POST /api/send-reset-email
    --------------------------
    Developer endpoint: looks up the given email in the database, generates a
    real password-reset token, saves it, and dispatches the actual branded
    reset email. Returns the exact Brevo API response for full visibility.

    Body: { "email": "user@example.com" }
    """
    import os
    from datetime import datetime, timezone, timedelta
    from flask import request as flask_request
    from ..extensions import db
    from ..models.user import User
    from ..services.email_service import send_password_reset_email
    from ..routes.auth import generate_reset_token

    data = flask_request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"error": "Provide {\"email\": \"user@example.com\"} in the request body"}), 400

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        return jsonify({
            "success": False,
            "error": f"No registered account found for {email}",
            "hint": "Register an account with this email first, or use an existing account email."
        }), 404

    # Generate and persist a real reset token
    token = generate_reset_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.session.commit()

    # Build the real reset URL (same as the forgot-password route)
    frontend_base = current_app.config.get(
        "FRONTEND_URL", "https://hydroponic-frontend-seven.vercel.app"
    ).rstrip("/")
    reset_url = f"{frontend_base}/pages/user/reset-password.html?token={token}"

    # Call the same email function used by forgot-password
    # This is synchronous — result is returned directly
    from ..services.email_service import _dispatch_email

    subject = "Reset Your AgriSmart AI Password"
    display_name = user.full_name or email

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
    <div class="h"><h1>&#127807; AgriSmart AI</h1><p>Intelligent Food Production Platform</p></div>
    <div class="b">
      <div class="g">Hello {display_name},</div>
      <div class="i">We received a request to reset the password for your AgriSmart AI account (<strong>{email}</strong>). Click the button below to set a new password:</div>
      <div class="bc"><a href="{reset_url}" class="btn" target="_blank">Reset My Password</a></div>
      <div class="n">&#9200; <strong>This link is valid for 1 hour.</strong> If you did not request a reset, ignore this email — your account is safe.</div>
      <div class="f">If the button does not work, copy this URL:<br><a href="{reset_url}" style="color:#059669">{reset_url}</a></div>
    </div>
    <div class="ft">&#169; 2026 AgriSmart AI. All rights reserved.</div>
  </div>
</body></html>"""

    text_body = f"""Hello {display_name},

Reset your AgriSmart AI password using this link (valid 1 hour):
{reset_url}

If you did not request this, ignore this email.

— AgriSmart AI Team
"""

    result = _dispatch_email(email, display_name, subject, html_body, text_body)

    return jsonify({
        "success": result.get("ok", False),
        "sent_to": email,           # The USER's email — where the reset link is sent
        "sent_from": os.environ.get("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com"),
        "reset_link": reset_url,
        "token_expires_in": "1 hour",
        "brevo_result": result,
    }), 200 if result.get("ok") else 500
