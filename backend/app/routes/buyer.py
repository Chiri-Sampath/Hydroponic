"""
AgriSmart AI — Buyer Portal Routes
====================================
Buyer profile management, requirement posting, inquiry submission and workflow.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.user import User
from ..models.market import BuyerProfile, BuyerRequirement, BuyerInquiry
from ..models.project import Project
from ..models.cultivation import Product
from ..utils.auth_decorators import require_active_user, roles_required

buyer_bp = Blueprint("buyer", __name__)


class BuyerProfileSchema(Schema):
    company_name = fields.Str(required=True, validate=validate.Length(min=2, max=300))
    business_type = fields.Str(load_default="Wholesaler / Processor")
    gstin = fields.Str(load_default=None)
    city = fields.Str(load_default=None)
    state = fields.Str(load_default=None)
    collection_radius_km = fields.Int(load_default=250)


class RequirementCreateSchema(Schema):
    product_id = fields.Int(required=True)
    required_quantity_kg_per_month = fields.Float(required=True)
    target_price_inr_per_kg = fields.Float(required=True)
    quality_grade = fields.Str(load_default="Grade A")
    cold_chain_required = fields.Boolean(load_default=False)
    packaging_requirements = fields.Str(load_default="")
    notes = fields.Str(load_default="")


class InquiryCreateSchema(Schema):
    buyer_requirement_id = fields.Int(required=True)
    producer_project_id = fields.Int(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=5, max=2000))


@buyer_bp.route("/profile", methods=["GET"])
@jwt_required()
@require_active_user
def get_buyer_profile():
    """GET /api/buyer/profile - Get current user's buyer business profile"""
    user_id = int(get_jwt_identity())
    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"success": True, "data": None}), 200

    return jsonify({
        "success": True,
        "data": {
            "id": profile.id,
            "company_name": profile.company_name,
            "business_type": profile.business_type,
            "gstin": profile.gstin,
            "city": profile.city,
            "state": profile.state,
            "collection_radius_km": profile.collection_radius_km,
            "verified": profile.verified,
        }
    }), 200


@buyer_bp.route("/profile", methods=["PUT", "POST"])
@jwt_required()
@require_active_user
def update_buyer_profile():
    """POST / PUT /api/buyer/profile - Update or create buyer profile"""
    user_id = int(get_jwt_identity())
    schema = BuyerProfileSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = BuyerProfile(user_id=user_id)
        db.session.add(profile)

    profile.company_name = data["company_name"]
    profile.business_type = data.get("business_type")
    profile.gstin = data.get("gstin")
    profile.city = data.get("city")
    profile.state = data.get("state")
    profile.collection_radius_km = data.get("collection_radius_km", 250)

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Buyer profile saved successfully",
        "data": {
            "id": profile.id,
            "company_name": profile.company_name,
            "business_type": profile.business_type,
        }
    }), 200


@buyer_bp.route("/requirements", methods=["GET"])
@jwt_required()
@require_active_user
def list_buyer_requirements():
    """GET /api/buyer/requirements - List posted buyer requirements"""
    user_id = int(get_jwt_identity())
    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"success": True, "data": []}), 200

    reqs = profile.requirements.filter_by(is_active=True).all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": r.id,
                "product_id": r.product_id,
                "product_name": db.session.get(Product, r.product_id).common_name if db.session.get(Product, r.product_id) else "Product",
                "required_monthly_kg": float(r.required_quantity_kg_per_month) if r.required_quantity_kg_per_month else None,
                "target_price_inr_per_kg": float(r.target_price_inr_per_kg) if r.target_price_inr_per_kg else None,
                "quality_grade": r.quality_grade,
                "cold_chain_required": r.cold_chain_required,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reqs
        ]
    }), 200


@buyer_bp.route("/requirements", methods=["POST"])
@jwt_required()
@require_active_user
def create_buyer_requirement():
    """POST /api/buyer/requirements - Post a new buyer requirement"""
    user_id = int(get_jwt_identity())
    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = BuyerProfile(user_id=user_id, company_name="Commercial Buyer")
        db.session.add(profile)
        db.session.flush()

    schema = RequirementCreateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    product = db.session.get(Product, data["product_id"])
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    req = BuyerRequirement(
        buyer_profile_id=profile.id,
        product_id=product.id,
        required_quantity_kg_per_month=data["required_quantity_kg_per_month"],
        target_price_inr_per_kg=data["target_price_inr_per_kg"],
        quality_grade=data.get("quality_grade", "Grade A"),
        cold_chain_required=data.get("cold_chain_required", False),
        packaging_requirements=data.get("packaging_requirements", ""),
        notes=data.get("notes", ""),
        is_active=True,
    )
    db.session.add(req)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Buyer requirement posted successfully",
        "data": {
            "id": req.id,
            "product_name": product.common_name,
            "required_monthly_kg": float(req.required_quantity_kg_per_month),
            "target_price_inr_per_kg": float(req.target_price_inr_per_kg),
        }
    }), 201


@buyer_bp.route("/requirements/<int:req_id>", methods=["PUT"])
@jwt_required()
@require_active_user
def update_buyer_requirement(req_id: int):
    """PUT /api/buyer/requirements/<id> - Update a posted buyer requirement"""
    user_id = int(get_jwt_identity())
    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"success": False, "error": "Buyer profile not found"}), 404

    req = db.session.get(BuyerRequirement, req_id)
    if not req or req.buyer_profile_id != profile.id:
        return jsonify({"success": False, "error": "Requirement not found"}), 404

    data = request.get_json(force=True) or {}
    if "required_quantity_kg_per_month" in data:
        req.required_quantity_kg_per_month = data["required_quantity_kg_per_month"]
    if "target_price_inr_per_kg" in data:
        req.target_price_inr_per_kg = data["target_price_inr_per_kg"]
    if "quality_grade" in data:
        req.quality_grade = data["quality_grade"]
    if "cold_chain_required" in data:
        req.cold_chain_required = data["cold_chain_required"]
    if "packaging_requirements" in data:
        req.packaging_requirements = data["packaging_requirements"]
    if "notes" in data:
        req.notes = data["notes"]
    if "is_active" in data:
        req.is_active = data["is_active"]

    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Requirement updated successfully",
        "data": {"id": req.id, "is_active": req.is_active}
    }), 200


@buyer_bp.route("/requirements/<int:req_id>", methods=["DELETE"])
@jwt_required()
@require_active_user
def delete_buyer_requirement(req_id: int):
    """DELETE /api/buyer/requirements/<id> - Soft delete or remove a buyer requirement"""
    user_id = int(get_jwt_identity())
    profile = BuyerProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({"success": False, "error": "Buyer profile not found"}), 404

    req = db.session.get(BuyerRequirement, req_id)
    if not req or req.buyer_profile_id != profile.id:
        return jsonify({"success": False, "error": "Requirement not found"}), 404

    req.is_active = False
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Buyer requirement deleted successfully"
    }), 200


@buyer_bp.route("/matches/<int:req_id>", methods=["GET"])
@jwt_required()
@require_active_user
def get_requirement_matches(req_id: int):
    """GET /api/buyer/matches/<id> - Find producer projects matching this requirement"""
    req = db.session.get(BuyerRequirement, req_id)
    if not req:
        return jsonify({"success": False, "error": "Requirement not found"}), 404

    projects = Project.query.filter(Project.status != "deleted").all()
    from .matching import calculate_match_metrics
    matches = [calculate_match_metrics(p, req) for p in projects]
    matches.sort(key=lambda x: x["cultivate_to_market_score"], reverse=True)

    return jsonify({
        "success": True,
        "data": matches,
        "meta": {"count": len(matches)}
    }), 200


@buyer_bp.route("/inquiries", methods=["POST"])
@jwt_required()
@require_active_user
def send_inquiry():
    """
    POST /api/buyer/inquiries
    -------------------------
    Submit a formal purchase inquiry to a producer.
    Transitions through: new -> contacted -> negotiating -> accepted -> rejected -> closed
    """
    schema = InquiryCreateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    req = db.session.get(BuyerRequirement, data["buyer_requirement_id"])
    proj = db.session.get(Project, data["producer_project_id"])

    if not req or not proj:
        return jsonify({"success": False, "error": "Buyer requirement or producer project not found"}), 404

    inquiry = BuyerInquiry(
        buyer_requirement_id=req.id,
        producer_project_id=proj.id,
        status="new",
        message=data["message"].strip(),
    )
    db.session.add(inquiry)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Inquiry submitted to producer successfully",
        "data": {
            "inquiry_id": inquiry.id,
            "status": inquiry.status,
            "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None,
        }
    }), 201
