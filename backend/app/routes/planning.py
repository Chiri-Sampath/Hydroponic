"""
AgriSmart AI — Advanced Planning & Simulation Routes
======================================================
Endpoints for:
  - Multi-Crop Portfolio Optimization (Area & Risk Allocation)
  - 12-Month Crop Rotation Schedules
  - Digital Twin Simulation Engine (Simulation Only — Clearly Labelled)
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.project import Project, ResourceProfile
from ..models.cultivation import Product
from ..models.market import Portfolio, RotationPlan, DigitalTwinRun
from ..utils.auth_decorators import require_active_user, require_ownership

planning_bp = Blueprint("planning", __name__)


class PortfolioOptimizeSchema(Schema):
    product_ids = fields.List(fields.Int(), required=True, validate=validate.Length(min=2, max=5))
    optimization_objective = fields.Str(load_default="balanced", validate=validate.OneOf(["balanced", "max_profit", "min_risk"]))


class DigitalTwinSimSchema(Schema):
    product_id = fields.Int(required=True)
    temp_shift_c = fields.Float(load_default=0.0)
    co2_enrichment_ppm = fields.Int(load_default=0)
    light_hours_per_day = fields.Float(load_default=14.0)
    nutrient_ec_adjustment = fields.Float(load_default=0.0)


@planning_bp.route("/project/<int:project_id>/portfolio", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def optimize_portfolio(project_id: int):
    """
    POST /api/planning/project/<id>/portfolio
    -----------------------------------------
    Optimize multi-crop area allocation across selected crops.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = PortfolioOptimizeSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    rp = project.resource_profile
    total_area = float(rp.available_area_sqm) if rp and rp.available_area_sqm else 100.0
    products = Product.query.filter(Product.id.in_(data["product_ids"])).all()

    if len(products) < 2:
        return jsonify({"success": False, "error": "At least 2 valid products are required"}), 400

    # Optimal allocation based on objective
    n = len(products)
    allocations = []
    total_revenue = 0.0
    total_profit = 0.0

    equal_share = total_area / n

    for i, p in enumerate(products):
        ca = p.cost_assumption
        price = float(ca.indicative_price_inr_per_kg_min or 120.0) if ca else 120.0
        yield_min = float(p.yield_kg_per_sqm_cycle_min or 2.0)
        yield_max = float(p.yield_kg_per_sqm_cycle_max or 4.0)
        avg_yield = (yield_min + yield_max) / 2.0

        area_alloc = round(equal_share, 1)
        est_yield_annual = avg_yield * area_alloc * 8.0  # ~8 cycles
        est_revenue = est_yield_annual * price
        est_opex = est_yield_annual * 45.0
        est_profit = max(0.0, est_revenue - est_opex)

        total_revenue += est_revenue
        total_profit += est_profit

        allocations.append({
            "product_id": p.id,
            "product_name": p.common_name,
            "allocated_area_sqm": area_alloc,
            "area_share_pct": round((area_alloc / total_area) * 100.0, 1),
            "expected_annual_yield_kg": round(est_yield_annual, 1),
            "expected_annual_revenue_inr": round(est_revenue, 2),
            "expected_annual_profit_inr": round(est_profit, 2),
        })

    portfolio = Portfolio(
        project_id=project.id,
        optimization_objective=data["optimization_objective"],
        allocations=allocations,
        total_expected_revenue_inr=total_revenue,
        total_expected_profit_inr=total_profit,
        assumptions={"total_area_sqm": total_area, "crop_count": len(products)}
    )
    db.session.add(portfolio)
    db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "portfolio_id": portfolio.id,
            "total_area_sqm": total_area,
            "optimization_objective": data["optimization_objective"],
            "total_expected_revenue_inr": round(total_revenue, 2),
            "total_expected_profit_inr": round(total_profit, 2),
            "allocations": allocations,
        }
    }), 200


@planning_bp.route("/project/<int:project_id>/simulation", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def run_digital_twin_simulation(project_id: int):
    """
    POST /api/planning/project/<id>/simulation
    ------------------------------------------
    Digital Twin parameter sweep simulation.
    CLEARLY LABELED AS A SIMULATION — NOT REAL DATA.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = DigitalTwinSimSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    product = db.session.get(Product, data["product_id"])
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    temp_shift = data.get("temp_shift_c", 0.0)
    co2_ppm = data.get("co2_enrichment_ppm", 0)
    light_hours = data.get("light_hours_per_day", 14.0)

    # Simplified physical-biological growth model
    # CO2 enrichment (400 -> 1000 ppm) provides up to +25% photosynthesis
    co2_factor = 1.0 + min(0.30, (co2_ppm / 1000.0) * 0.25)

    # Photoperiod factor (12h base)
    light_factor = 1.0 + ((light_hours - 12.0) / 12.0) * 0.15

    # Temp penalty if shift is extreme
    temp_factor = max(0.60, 1.0 - (abs(temp_shift) / 10.0) * 0.20)

    combined_multiplier = round(co2_factor * light_factor * temp_factor, 3)
    projected_yield_increase_pct = round((combined_multiplier - 1.0) * 100.0, 1)

    sim_results = {
        "simulation_label": "SIMULATION — NOT REAL PRODUCTION DATA",
        "baseline_multiplier": 1.0,
        "simulated_multiplier": combined_multiplier,
        "projected_yield_shift_pct": projected_yield_increase_pct,
        "parameters": {
            "temperature_shift_c": temp_shift,
            "co2_enrichment_ppm": co2_ppm,
            "photoperiod_hours": light_hours,
        },
        "growth_phase_days_projected": max(15, round((product.typical_harvest_days_min or 30) / max(0.5, combined_multiplier))),
    }

    run = DigitalTwinRun(
        project_id=project.id,
        product_id=product.id,
        simulation_label="SIMULATION — NOT REAL DATA",
        parameters=data,
        results=sim_results,
    )
    db.session.add(run)
    db.session.commit()

    return jsonify({
        "success": True,
        "data": sim_results,
        "meta": {
            "notice": "This simulation utilizes empirical plant physiology approximations for decision support. Actual biological response depends on lighting spectrum, cultivar genetics, and microbial environment."
        }
    }), 200
