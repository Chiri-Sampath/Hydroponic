"""
AgriSmart AI — Economics Routes
=================================
Endpoints for:
  - Base project financial summary
  - What-If Scenario simulation
  - Scenario list & comparison
  - Break-Even Analysis
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.project import Project, ResourceProfile
from ..models.cultivation import Product
from ..models.recommendation import Scenario, BreakEvenRun
from ..services.economics_service import calculate_detailed_economics
from ..utils.auth_decorators import require_active_user, require_ownership

economics_bp = Blueprint("economics", __name__)


class ScenarioRunSchema(Schema):
    product_id = fields.Int(required=True)
    scenario_type = fields.Str(load_default="what_if", validate=validate.OneOf(["base", "what_if", "portfolio"]))
    scenario_name = fields.Str(load_default=None)
    area_sqm = fields.Float(load_default=None)
    selling_price_inr_per_kg = fields.Float(load_default=None)
    yield_override_kg = fields.Float(load_default=None)
    electricity_inr_per_kg = fields.Float(load_default=None)
    labor_inr_per_kg = fields.Float(load_default=None)
    water_inr_per_kg = fields.Float(load_default=None)
    nutrients_inr_per_kg = fields.Float(load_default=None)
    packaging_inr_per_kg = fields.Float(load_default=None)
    transport_inr_per_kg = fields.Float(load_default=None)
    save_scenario = fields.Boolean(load_default=False)


@economics_bp.route("/project/<int:project_id>/scenario", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def run_scenario(project_id: int):
    """
    POST /api/economics/project/<id>/scenario
    -----------------------------------------
    Run a financial scenario or What-If simulation for a project.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = ScenarioRunSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    product = db.session.get(Product, data["product_id"])
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    # Determine area
    rp = project.resource_profile
    area_sqm = data.get("area_sqm") or (float(rp.available_area_sqm) if rp and rp.available_area_sqm else 50.0)

    cost_overrides = {
        "electricity_inr_per_kg": data.get("electricity_inr_per_kg"),
        "labor_inr_per_kg": data.get("labor_inr_per_kg"),
        "water_inr_per_kg": data.get("water_inr_per_kg"),
        "nutrients_inr_per_kg": data.get("nutrients_inr_per_kg"),
        "packaging_inr_per_kg": data.get("packaging_inr_per_kg"),
        "transport_inr_per_kg": data.get("transport_inr_per_kg"),
    }

    result = calculate_detailed_economics(
        product=product,
        area_sqm=area_sqm,
        selling_price_override=data.get("selling_price_inr_per_kg"),
        yield_override_kg=data.get("yield_override_kg"),
        cost_overrides=cost_overrides,
    )

    # Save scenario if requested
    saved_scenario_id = None
    if data.get("save_scenario"):
        sc = Scenario(
            project_id=project.id,
            product_id=product.id,
            scenario_type=data.get("scenario_type", "what_if"),
            name=data.get("scenario_name") or f"{product.common_name} — {data.get('scenario_type', 'What-If')}",
            area_sqm=area_sqm,
            selling_price_inr_per_kg=result["selling_price_per_kg_inr"],
            yield_kg=result["annual_yield_kg"],
            revenue_inr=result["annual_revenue_inr"],
            opex_inr=result["opex_breakdown"]["total_annual_opex_inr"],
            profit_inr=result["annual_gross_profit_inr"],
            roi_pct=result["annual_roi_pct"],
            assumptions=result["disclaimer"]
        )
        db.session.add(sc)
        db.session.commit()
        saved_scenario_id = sc.id

    return jsonify({
        "success": True,
        "data": {
            **result,
            "saved_scenario_id": saved_scenario_id,
        }
    }), 200


@economics_bp.route("/project/<int:project_id>/scenarios", methods=["GET"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def list_scenarios(project_id: int):
    """GET /api/economics/project/<id>/scenarios - List saved financial scenarios"""
    scenarios = Scenario.query.filter_by(project_id=project_id).order_by(Scenario.created_at.desc()).all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": s.id,
                "name": s.name,
                "scenario_type": s.scenario_type,
                "product_id": s.product_id,
                "area_sqm": float(s.area_sqm) if s.area_sqm else None,
                "selling_price_inr_per_kg": float(s.selling_price_inr_per_kg) if s.selling_price_inr_per_kg else None,
                "revenue_inr": float(s.revenue_inr) if s.revenue_inr else None,
                "profit_inr": float(s.profit_inr) if s.profit_inr else None,
                "roi_pct": float(s.roi_pct) if s.roi_pct else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in scenarios
        ]
    }), 200
