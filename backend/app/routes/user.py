"""
AgriSmart AI — User & Project Routes
======================================
Handles user profiles, project CRUD operations, and resource/objective bindings.
Ownership is strictly enforced on all project operations.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.user import User, UserProfile, AuditLog
from ..models.project import Project, Location, ResourceProfile, Objective
from ..utils.auth_decorators import require_active_user, require_ownership

user_bp = Blueprint("user", __name__)


# ── Schemas ──────────────────────────────────────────────────────────────────

class ProfileUpdateSchema(Schema):
    full_name = fields.Str(validate=validate.Length(max=200))
    phone = fields.Str(validate=validate.Length(max=20))
    organization = fields.Str(validate=validate.Length(max=200))
    bio = fields.Str(validate=validate.Length(max=1000))


class ProjectCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    description = fields.Str(load_default="", validate=validate.Length(max=2000))


class ProjectUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2, max=200))
    description = fields.Str(validate=validate.Length(max=2000))
    status = fields.Str(validate=validate.OneOf(["active", "archived", "deleted"]))


# ── Helpers ───────────────────────────────────────────────────────────────────

def _project_to_dict(project: Project, include_details: bool = True) -> dict:
    data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
    }

    if include_details:
        # Location
        if project.location:
            data["location"] = {
                "id": project.location.id,
                "raw_input": project.location.raw_input,
                "display_name": project.location.display_name,
                "latitude": float(project.location.latitude) if project.location.latitude is not None else None,
                "longitude": float(project.location.longitude) if project.location.longitude is not None else None,
                "country": project.location.country,
                "state": project.location.state,
                "city": project.location.city,
                "geocoded_at": project.location.geocoded_at.isoformat() if project.location.geocoded_at else None,
                "has_weather": project.location.current_weather is not None,
                "weather_source": project.location.weather_source,
                "weather_retrieved_at": project.location.weather_retrieved_at.isoformat() if project.location.weather_retrieved_at else None,
            }
        else:
            data["location"] = None

        # Resource Profile
        if project.resource_profile:
            rp = project.resource_profile
            data["resources"] = {
                "id": rp.id,
                "available_area_sqm": float(rp.available_area_sqm) if rp.available_area_sqm is not None else None,
                "area_type": rp.area_type,
                "available_capital_inr": float(rp.available_capital_inr) if rp.available_capital_inr is not None else None,
                "water_available_litres_day": float(rp.water_available_litres_day) if rp.water_available_litres_day is not None else None,
                "water_constraints": rp.water_constraints,
                "manpower_workers": rp.manpower_workers,
                "manpower_hours_per_day": float(rp.manpower_hours_per_day) if rp.manpower_hours_per_day is not None else None,
                "existing_infrastructure": rp.existing_infrastructure or [],
            }
        else:
            data["resources"] = None

        # Objective
        if project.objective:
            obj = project.objective
            data["objective"] = {
                "id": obj.id,
                "objective_type": obj.objective_type,
                "secondary_objective": obj.secondary_objective,
                "notes": obj.notes,
            }
        else:
            data["objective"] = None

        # Latest recommendation summary
        latest_run = project.recommendation_runs.order_by(db.desc("created_at")).first()
        if latest_run:
            top_rec = latest_run.results.filter_by(is_recommended=True).first()
            data["latest_recommendation"] = {
                "run_id": latest_run.id,
                "status": latest_run.status,
                "created_at": latest_run.created_at.isoformat() if latest_run.created_at else None,
                "top_product": top_rec.product.common_name if (top_rec and top_rec.product) else None,
                "suitability_score": float(top_rec.suitability_score) if (top_rec and top_rec.suitability_score) else None,
            }
        else:
            data["latest_recommendation"] = None

    return data


# ── Profile Endpoints ─────────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["GET"])
@jwt_required()
@require_active_user
def get_profile():
    """GET /api/users/profile - Current user profile"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    profile = user.profile
    return jsonify({
        "success": True,
        "data": {
            "id": user.id,
            "email": user.email,
            "role": user.role.name,
            "role_display": user.role.display_name,
            "status": user.status,
            "full_name": profile.full_name if profile else None,
            "phone": profile.phone if profile else None,
            "organization": profile.organization if profile else None,
            "bio": profile.bio if profile else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
@require_active_user
def update_profile():
    """PUT /api/users/profile - Update user profile"""
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    schema = ProfileUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)

    if "full_name" in data:
        profile.full_name = data["full_name"]
    if "phone" in data:
        profile.phone = data["phone"]
    if "organization" in data:
        profile.organization = data["organization"]
    if "bio" in data:
        profile.bio = data["bio"]

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Profile updated successfully",
        "data": {
            "id": user.id,
            "email": user.email,
            "full_name": profile.full_name,
            "phone": profile.phone,
            "organization": profile.organization,
            "bio": profile.bio,
        }
    }), 200


# ── Projects Endpoints ────────────────────────────────────────────────────────

@user_bp.route("/projects", methods=["GET"])
@jwt_required()
@require_active_user
def list_projects():
    """GET /api/users/projects - List all projects owned by authenticated user"""
    user_id = int(get_jwt_identity())
    projects = Project.query.filter_by(user_id=user_id, status="active").order_by(Project.updated_at.desc()).all()
    return jsonify({
        "success": True,
        "data": [_project_to_dict(p, include_details=True) for p in projects],
        "meta": {"count": len(projects)}
    }), 200


@user_bp.route("/projects", methods=["POST"])
@jwt_required()
@require_active_user
def create_project():
    """POST /api/users/projects - Create a new cultivation project"""
    user_id = int(get_jwt_identity())
    schema = ProjectCreateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    project = Project(
        user_id=user_id,
        name=data["name"].strip(),
        description=data.get("description", "").strip(),
        status="active",
    )
    db.session.add(project)
    db.session.commit()

    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="project.create",
        target_type="Project",
        target_id=project.id,
        details={"name": project.name},
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Project created successfully",
        "data": _project_to_dict(project, include_details=True)
    }), 201


@user_bp.route("/projects/<int:project_id>", methods=["GET"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def get_project(project_id: int):
    """GET /api/users/projects/<id> - Get specific project details"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    return jsonify({
        "success": True,
        "data": _project_to_dict(project, include_details=True)
    }), 200


@user_bp.route("/projects/<int:project_id>", methods=["PUT"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def update_project(project_id: int):
    """PUT /api/users/projects/<id> - Update project name, description or status"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = ProjectUpdateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    if "name" in data:
        project.name = data["name"].strip()
    if "description" in data:
        project.description = data["description"].strip()
    if "status" in data:
        project.status = data["status"]

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Project updated successfully",
        "data": _project_to_dict(project, include_details=True)
    }), 200


@user_bp.route("/projects/<int:project_id>", methods=["DELETE"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def delete_project(project_id: int):
    """DELETE /api/users/projects/<id> - Soft delete / archive project"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    project.status = "deleted"
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Project deleted successfully"
    }), 200
