"""
AgriSmart AI — Admin & Governance Routes
==========================================
System administration, user lifecycle management, audit trail inspection,
data source registry, and system settings configuration.
All endpoints strictly require the 'admin' role.
"""

import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.user import User, Role, UserProfile, AuditLog
from ..models.project import Project, Location
from ..models.recommendation import RecommendationRun, ModelVersion, RecommendationResult
from ..models.quality import LabReport, Laboratory, Batch
from ..models.cultivation import Product
from ..models.market import DataSource, SystemSetting
from ..utils.auth_decorators import require_active_user, roles_required
from ..utils.security import hash_password

admin_bp = Blueprint("admin", __name__)


def is_primary_admin(user: User) -> bool:
    """Check if the user is the Primary / Root Platform Administrator."""
    if not user or not user.email:
        return False
    primary_emails = {
        os.environ.get("ADMIN_EMAIL", "admin@agrismart.local").strip().lower(),
        "admin@agrismart.local",
        "admin@agrismart.ai",
        "admin@test.local",
    }
    return user.email.strip().lower() in primary_emails


class GrantAdminSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.Str(load_default="Platform Administrator")
    initial_password = fields.Str(load_default="Admin@12345")


class RevokeAdminSchema(Schema):
    email = fields.Email(required=False)
    user_id = fields.Int(required=False)


class UserStatusUpdateSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(["active", "suspended", "deactivated"]))
    reason = fields.Str(load_default="")


class SystemSettingUpdateSchema(Schema):
    value = fields.Str(required=True)


@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def get_admin_dashboard():
    """
    GET /api/admin/dashboard
    ------------------------
    Executive platform overview with user counts, active projects, recommendation runs,
    and audit activity metrics.
    """
    total_users = User.query.count()
    active_users = User.query.filter_by(status="active").count()
    total_projects = Project.query.filter(Project.status != "deleted").count()
    total_runs = RecommendationRun.query.count()
    total_reports = LabReport.query.count()
    total_labs = Laboratory.query.count()

    recent_audits = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()

    return jsonify({
        "success": True,
        "data": {
            "metrics": {
                "total_users": total_users,
                "active_users": active_users,
                "total_projects": total_projects,
                "total_recommendations": total_runs,
                "total_lab_reports": total_reports,
                "total_laboratories": total_labs,
            },
            "recent_activity": [
                {
                    "id": a.id,
                    "action": a.action,
                    "user_id": a.user_id,
                    "target_type": a.target_type,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "ip": a.ip_address,
                }
                for a in recent_audits
            ]
        }
    }), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_users():
    """GET /api/admin/users - List all registered platform users with their linked cultivation projects"""
    users = User.query.order_by(User.created_at.desc()).all()
    user_list = []
    for u in users:
        active_projects = u.projects.filter(Project.status != "deleted").all() if hasattr(u, "projects") and hasattr(u.projects, "filter") else []
        user_list.append({
            "id": u.id,
            "email": u.email,
            "role": u.role.name if u.role else None,
            "role_display": u.role.display_name if u.role else None,
            "is_main_admin": is_primary_admin(u),
            "status": u.status,
            "full_name": u.profile.full_name if u.profile else None,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "projects_count": len(active_projects),
            "projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "status": p.status,
                    "location": (p.location.city if (p.location and p.location.city) else (p.location.display_name if (p.location and p.location.display_name) else (p.location.raw_input if p.location else "Not specified"))),
                    "area_sqm": float(p.resource_profile.available_area_sqm) if p.resource_profile and p.resource_profile.available_area_sqm else None,
                    "batches_count": p.batches.count() if hasattr(p, "batches") else 0,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in active_projects
            ]
        })

    return jsonify({
        "success": True,
        "data": user_list,
        "meta": {"count": len(user_list)}
    }), 200


@admin_bp.route("/users/grant-admin", methods=["POST"])
@jwt_required()
@require_active_user
@roles_required("admin")
def grant_admin_access():
    """
    POST /api/admin/users/grant-admin
    ---------------------------------
    Grant administrator role to any user via their email address.
    If the user is already registered, elevates their role to 'admin'.
    If the user does not exist, registers a new Administrator account.
    """
    schema = GrantAdminSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    target_email = data["email"].strip().lower()
    full_name = data.get("full_name", "Platform Administrator").strip() or "Platform Administrator"
    initial_password = data.get("initial_password", "Admin@12345")
    current_admin_id = int(get_jwt_identity())

    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        return jsonify({"success": False, "error": "Admin role configuration not found"}), 500

    user = User.query.filter_by(email=target_email).first()

    if user:
        old_role = user.role.name if user.role else "none"
        if user.role_id == admin_role.id:
            return jsonify({
                "success": True,
                "message": f"User '{target_email}' already has Administrator privileges.",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "role": "admin",
                    "full_name": user.profile.full_name if user.profile else full_name,
                    "status": user.status,
                    "is_new": False,
                }
            }), 200

        user.role_id = admin_role.id
        if not user.profile:
            user.profile = UserProfile(user=user, full_name=full_name, organization="AgriSmart Administration")
        elif not user.profile.full_name:
            user.profile.full_name = full_name

        audit = AuditLog(
            user_id=current_admin_id,
            action="admin.user.grant_admin",
            target_type="User",
            target_id=user.id,
            details={"target_email": target_email, "old_role": old_role, "new_role": "admin"},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Successfully elevated '{target_email}' from '{old_role}' to Administrator.",
            "data": {
                "id": user.id,
                "email": user.email,
                "role": "admin",
                "full_name": user.profile.full_name,
                "status": user.status,
                "is_new": False,
            }
        }), 200
    else:
        # Create new admin user
        hashed = hash_password(initial_password)
        new_user = User(
            email=target_email,
            password_hash=hashed,
            role_id=admin_role.id,
            status="active",
            email_verified=True,
        )
        db.session.add(new_user)
        db.session.flush()

        profile = UserProfile(
            user_id=new_user.id,
            full_name=full_name,
            organization="AgriSmart Administration",
        )
        db.session.add(profile)

        audit = AuditLog(
            user_id=current_admin_id,
            action="admin.user.create_admin",
            target_type="User",
            target_id=new_user.id,
            details={"target_email": target_email, "role": "admin"},
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")[:500],
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Created new Administrator account for '{target_email}' (Temporary password: {initial_password}).",
            "data": {
                "id": new_user.id,
                "email": new_user.email,
                "role": "admin",
                "full_name": profile.full_name,
                "status": new_user.status,
                "is_new": True,
                "initial_password": initial_password,
            }
        }), 201


@admin_bp.route("/users/revoke-admin", methods=["POST"])
@jwt_required()
@require_active_user
@roles_required("admin")
def revoke_admin_access():
    """
    POST /api/admin/users/revoke-admin
    ----------------------------------
    Revoke administrator privileges from an admin user.
    Strictly restricted to the Main (Primary) Administrator.
    Reverts the user's role to 'general_user'.
    """
    current_admin_id = int(get_jwt_identity())
    current_admin = db.session.get(User, current_admin_id)
    if not current_admin or not is_primary_admin(current_admin):
        return jsonify({
            "success": False,
            "error": "Forbidden",
            "message": "Only the Primary Administrator (Main Admin) has permission to remove administrator access."
        }), 403

    schema = RevokeAdminSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    target_email = (data.get("email") or "").strip().lower()
    target_id = data.get("user_id")

    user = None
    if target_id:
        user = db.session.get(User, int(target_id))
    elif target_email:
        user = User.query.filter_by(email=target_email).first()

    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    if user.id == current_admin.id:
        return jsonify({"success": False, "error": "Cannot remove your own administrator privileges"}), 400

    if is_primary_admin(user):
        return jsonify({"success": False, "error": "Cannot remove the Primary Administrator account"}), 400

    general_role = Role.query.filter_by(name="general_user").first()
    if not general_role:
        return jsonify({"success": False, "error": "General User role not found"}), 500

    old_role = user.role.name if user.role else "admin"
    user.role_id = general_role.id

    audit = AuditLog(
        user_id=current_admin_id,
        action="admin.user.revoke_admin",
        target_type="User",
        target_id=user.id,
        details={"target_email": user.email, "old_role": old_role, "new_role": "general_user"},
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Successfully revoked administrator privileges from '{user.email}'. Account reverted to General User.",
        "data": {
            "id": user.id,
            "email": user.email,
            "role": "general_user",
            "role_display": general_role.display_name,
            "full_name": user.profile.full_name if user.profile else None,
            "status": user.status,
        }
    }), 200


@admin_bp.route("/users/<int:user_id>/status", methods=["PATCH"])
@jwt_required()
@require_active_user
@roles_required("admin")
def update_user_status(user_id: int):
    """
    PATCH /api/admin/users/<id>/status
    ----------------------------------
    Suspend, activate, or deactivate a user account.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    # Prevent suspending self
    current_admin_id = int(get_jwt_identity())
    if user.id == current_admin_id:
        return jsonify({"success": False, "error": "Cannot change your own account status"}), 400

    schema = UserStatusUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    old_status = user.status
    user.status = data["status"]

    # Write audit log
    audit = AuditLog(
        user_id=current_admin_id,
        action=f"admin.user.{data['status']}",
        target_type="User",
        target_id=user.id,
        details={"old_status": old_status, "new_status": user.status, "reason": data.get("reason")},
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"User {user.email} status updated to '{user.status}'",
        "data": {"id": user.id, "email": user.email, "status": user.status}
    }), 200


@admin_bp.route("/audit", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_audit_logs():
    """GET /api/admin/audit?page=1 - View immutable security audit logs"""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return jsonify({
        "success": True,
        "data": [
            {
                "id": a.id,
                "action": a.action,
                "user_id": a.user_id,
                "target_type": a.target_type,
                "target_id": a.target_id,
                "details": a.details,
                "ip_address": a.ip_address,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in items
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
        }
    }), 200


@admin_bp.route("/sources", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_data_sources():
    """GET /api/admin/sources - View external data source governance registry"""
    sources = DataSource.query.all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "source_type": s.source_type,
                "url": s.url,
                "attribution": s.attribution,
                "license": s.license,
                "last_verified": s.last_verified.isoformat() if s.last_verified else None,
            }
            for s in sources
        ]
    }), 200


@admin_bp.route("/settings", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_settings():
    """GET /api/admin/settings - View system configuration settings"""
    settings = SystemSetting.query.all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": s.id,
                "key": s.key,
                "value": s.value,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            }
            for s in settings
        ]
    }), 200


@admin_bp.route("/settings/<string:key>", methods=["PUT"])
@jwt_required()
@require_active_user
@roles_required("admin")
def update_setting(key: str):
    """PUT /api/admin/settings/<key> - Update a system configuration setting"""
    setting = SystemSetting.query.filter_by(key=key).first()
    if not setting:
        return jsonify({"success": False, "error": f"Setting '{key}' not found"}), 404

    schema = SystemSettingUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    admin_id = int(get_jwt_identity())
    setting.value = data["value"]
    setting.updated_by_user_id = admin_id
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Setting '{key}' updated successfully",
        "data": {"key": setting.key, "value": setting.value}
    }), 200


@admin_bp.route("/projects", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_admin_projects():
    """GET /api/admin/projects - List all active projects across the platform with owner details"""
    projects = Project.query.filter(Project.status != "deleted").order_by(Project.created_at.desc()).all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "status": p.status,
                "user_id": p.user_id,
                "owner_email": p.user.email if p.user else "Unknown",
                "owner_name": p.user.profile.full_name if p.user and p.user.profile else "Producer",
                "location": (p.location.city if (p.location and p.location.city) else (p.location.display_name if (p.location and p.location.display_name) else (p.location.raw_input if p.location else "Not specified"))),
                "area_sqm": float(p.resource_profile.available_area_sqm) if p.resource_profile and p.resource_profile.available_area_sqm else None,
                "batches_count": p.batches.count(),
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ],
        "meta": {"count": len(projects)}
    }), 200


@admin_bp.route("/recommendations", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_admin_recommendations():
    """GET /api/admin/recommendations - List AI recommendation runs across active projects"""
    runs = RecommendationRun.query.join(Project).filter(Project.status != "deleted").order_by(RecommendationRun.created_at.desc()).all()
    out = []
    for r in runs:
        top_res = r.results.order_by(RecommendationResult.rank.asc()).first()
        out.append({
            "id": r.id,
            "project_id": r.project_id,
            "project_name": r.project.name if r.project else f"Project #{r.project_id}",
            "owner_email": r.project.user.email if r.project and r.project.user else "Unknown",
            "objective_type": r.objective_type,
            "top_crop": top_res.product.common_name if top_res and top_res.product else "N/A",
            "suitability_score": float(top_res.suitability_score) if top_res and top_res.suitability_score else None,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return jsonify({
        "success": True,
        "data": out,
        "meta": {"count": len(out)}
    }), 200


@admin_bp.route("/lab-reports", methods=["GET"])
@jwt_required()
@require_active_user
@roles_required("admin")
def list_admin_lab_reports():
    """GET /api/admin/lab-reports - List all processed laboratory quality reports"""
    reports = LabReport.query.order_by(LabReport.created_at.desc()).all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": rep.id,
                "batch_id": rep.batch_id,
                "batch_code": rep.batch.batch_code if rep.batch else "—",
                "product_name": rep.batch.product.common_name if rep.batch and rep.batch.product else "Cultivation Crop",
                "project_name": rep.batch.project.name if rep.batch and rep.batch.project else "—",
                "owner_email": rep.batch.project.user.email if rep.batch and rep.batch.project and rep.batch.project.user else "—",
                "lab_name": rep.laboratory.name if (rep.laboratory and hasattr(rep.laboratory, 'name')) else "Certified Lab Partner",
                "overall_status": rep.batch.quality_passport.overall_status if (rep.batch and rep.batch.quality_passport) else (rep.ocr_status or "Verified"),
                "report_number": (rep.ocr_extracted.get("report_number") if (rep.ocr_extracted and isinstance(rep.ocr_extracted, dict)) else None) or f"REP-{rep.id:04d}",
                "test_date": rep.report_date.isoformat() if rep.report_date else (rep.created_at.strftime("%Y-%m-%d") if rep.created_at else None),
                "created_at": rep.created_at.isoformat() if rep.created_at else None,
            }
            for rep in reports
        ],
        "meta": {"count": len(reports)}
    }), 200

