"""
AgriSmart AI — Recommendation Engine Routes
==============================================
Orchestrates:
  1. Feasibility Filter (Layer 1)
  2. Suitability Scoring (Layer 2) with objective weights
  3. Feature Importance & Explainability (Why This / Not That)
  4. Yield, OPEX, Revenue, and ROI estimation
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import Schema, fields, validate, ValidationError

from ..extensions import db
from ..models.project import Project, ResourceProfile, Objective
from ..models.cultivation import Product
from ..models.recommendation import RecommendationRun, RecommendationResult, FeatureImportance
from ..ml.inference.feasibility_engine import evaluate_feasibility
from ..ml.inference.suitability_engine import calculate_suitability_score
from ..ml.explainability.explainer import generate_feature_explanations, generate_comparison_explanation
from ..services.weather_service import fetch_weather
from ..utils.auth_decorators import require_active_user, require_ownership

recommendation_bp = Blueprint("recommendation", __name__)


class RunRecommendationSchema(Schema):
    objective_type = fields.Str(
        load_default=None,
        validate=validate.OneOf(Objective.OBJECTIVE_TYPES)
    )
    # Optional direct overrides for resources (if not yet saved on project)
    available_area_sqm = fields.Float(load_default=None)
    area_type = fields.Str(load_default=None)
    available_capital_inr = fields.Float(load_default=None)
    water_available_litres_day = fields.Float(load_default=None)
    manpower_workers = fields.Int(load_default=None)


def _serialize_result(r: RecommendationResult, detailed: bool = True) -> dict:
    p = r.product
    data = {
        "id": r.id,
        "product_id": r.product_id,
        "product_name": p.common_name if p else "Unknown",
        "scientific_name": p.scientific_name if p else None,
        "method_name": p.method.name if (p and p.method) else None,
        "method_display": p.method.display_name if (p and p.method) else None,
        "rank": r.rank,
        "is_recommended": r.is_recommended,
        "feasible": r.feasible,
        "feasibility_notes": r.feasibility_notes or [],
        "suitability_score": float(r.suitability_score) if r.suitability_score is not None else 0.0,
        "component_scores": r.component_scores or {},
        "estimated_yield_kg": float(r.estimated_yield_kg) if r.estimated_yield_kg is not None else 0.0,
        "estimated_revenue_inr": float(r.estimated_revenue_inr) if r.estimated_revenue_inr is not None else 0.0,
        "estimated_opex_inr": float(r.estimated_opex_inr) if r.estimated_opex_inr is not None else 0.0,
        "estimated_profit_inr": float(r.estimated_profit_inr) if r.estimated_profit_inr is not None else 0.0,
        "estimated_roi_pct": float(r.estimated_roi_pct) if r.estimated_roi_pct is not None else 0.0,
        "risk_score": float(r.risk_score) if r.risk_score is not None else 75.0,
        "sustainability_score": float(r.sustainability_score) if r.sustainability_score is not None else 80.0,
        "assumptions": r.assumptions or [
            "All yield and financial figures are indicative estimates for decision support.",
            "Actual results vary with operating conditions, grower skill, and market dynamics."
        ],
    }

    if detailed:
        data["feature_importance"] = [
            {
                "feature_name": fi.feature_name,
                "importance_value": float(fi.importance_value) if fi.importance_value is not None else 0.0,
                "direction": fi.direction,
                "human_explanation": fi.human_explanation,
            }
            for fi in r.feature_importance
        ]

    return data


@recommendation_bp.route("/run/<int:project_id>", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def run_recommendation(project_id: int):
    """
    POST /api/recommendations/run/<project_id>
    -----------------------------------------
    Run two-layer AI recommendation for a project.
    Evaluates all active products, ranks them, produces explainability,
    and returns comprehensive recommendation results.
    """
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = RunRecommendationSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    # Get or update resource profile
    rp = project.resource_profile
    if not rp:
        rp = ResourceProfile(project_id=project.id)
        db.session.add(rp)

    if data.get("available_area_sqm") is not None:
        rp.available_area_sqm = data["available_area_sqm"]
    if data.get("area_type") is not None:
        rp.area_type = data["area_type"]
    if data.get("available_capital_inr") is not None:
        rp.available_capital_inr = data["available_capital_inr"]
    if data.get("water_available_litres_day") is not None:
        rp.water_available_litres_day = data["water_available_litres_day"]
    if data.get("manpower_workers") is not None:
        rp.manpower_workers = data["manpower_workers"]

    # Get or update objective
    obj = project.objective
    if not obj:
        obj = Objective(project_id=project.id, objective_type=data.get("objective_type") or "let_ai_decide")
        db.session.add(obj)
    elif data.get("objective_type"):
        obj.objective_type = data["objective_type"]

    objective_type = obj.objective_type or "let_ai_decide"

    # Get weather data for project location
    weather_data = {}
    if project.location and project.location.latitude and project.location.longitude:
        if project.location.current_weather:
            weather_data = {
                "current": project.location.current_weather,
                "forecast_7day": project.location.forecast,
                "climate_profile": project.location.historical_climate,
            }
        else:
            weather_data = fetch_weather(float(project.location.latitude), float(project.location.longitude))
    else:
        # Default representative baseline weather
        weather_data = {
            "current": {"temperature_c": 24.0, "humidity_pct": 60.0, "solar_radiation_w_m2": 450.0},
            "forecast_7day": [],
            "climate_profile": {"climate_zone": "Tropical / Subtropical"},
        }

    # Fetch all active products
    products = Product.query.filter_by(is_active=True).all()
    if not products:
        return jsonify({"success": False, "error": "No active products found in knowledge base"}), 500

    # Create RecommendationRun record
    run = RecommendationRun(
        project_id=project.id,
        objective_type=objective_type,
        status="pending",
        input_snapshot={
            "area_sqm": float(rp.available_area_sqm) if rp.available_area_sqm else 50.0,
            "area_type": rp.area_type or "outdoor",
            "capital_inr": float(rp.available_capital_inr) if rp.available_capital_inr else 150000.0,
            "water_litres_day": float(rp.water_available_litres_day) if rp.water_available_litres_day else 500.0,
            "objective": objective_type,
            "location": project.location.display_name if project.location else "Not specified",
        }
    )
    db.session.add(run)
    db.session.flush()

    area_sqm = float(rp.available_area_sqm) if rp.available_area_sqm else 50.0

    product_evaluations = []

    for p in products:
        # Layer 1: Feasibility
        is_feasible, feas_reasons, checks = evaluate_feasibility(p, rp, weather_data)

        # Layer 2: Suitability Score
        score, comp_scores, weights = calculate_suitability_score(p, rp, weather_data, objective_type)

        # If not feasible, apply penalty to overall score
        effective_score = score if is_feasible else min(score, 45.0)

        # Yield and Economics Estimates
        yield_min = float(p.yield_kg_per_sqm_cycle_min) if p.yield_kg_per_sqm_cycle_min else 2.0
        yield_max = float(p.yield_kg_per_sqm_cycle_max) if p.yield_kg_per_sqm_cycle_max else 4.0
        avg_yield_per_sqm = (yield_min + yield_max) / 2.0
        cycle_yield_kg = avg_yield_per_sqm * area_sqm

        days = (p.typical_harvest_days_min or 30 + (p.typical_harvest_days_max or 45)) / 2.0
        cycles_per_year = max(1.0, 330.0 / max(10.0, days))
        annual_yield_kg = cycle_yield_kg * cycles_per_year

        ca = p.cost_assumption
        price_per_kg = float(ca.indicative_price_inr_per_kg_min) if (ca and ca.indicative_price_inr_per_kg_min) else 120.0
        total_revenue = annual_yield_kg * price_per_kg

        opex_per_kg = (
            float(ca.electricity_inr_per_kg or 10.0) +
            float(ca.water_inr_per_kg or 3.0) +
            float(ca.nutrients_inr_per_kg or 8.0) +
            float(ca.labor_inr_per_kg or 15.0) +
            float(ca.packaging_inr_per_kg or 5.0)
        ) if ca else 45.0
        total_opex = annual_yield_kg * opex_per_kg
        annual_profit = max(0.0, total_revenue - total_opex)

        infra = p.infrastructure
        capex_sqm = float(infra.estimated_capex_inr_per_sqm_min) if (infra and infra.estimated_capex_inr_per_sqm_min) else 800.0
        total_capex = capex_sqm * area_sqm
        roi_pct = (annual_profit / max(1.0, total_capex)) * 100.0

        # Generate Explainability / Feature Importance
        explanations = generate_feature_explanations(p, comp_scores, weights, objective_type, is_feasible)

        product_evaluations.append({
            "product": p,
            "is_feasible": is_feasible,
            "feas_reasons": feas_reasons,
            "score": effective_score,
            "comp_scores": comp_scores,
            "weights": weights,
            "cycle_yield_kg": round(cycle_yield_kg, 2),
            "annual_yield_kg": round(annual_yield_kg, 2),
            "revenue": round(total_revenue, 2),
            "opex": round(total_opex, 2),
            "profit": round(annual_profit, 2),
            "roi_pct": round(roi_pct, 1),
            "risk_score": comp_scores.get("risk", 75.0),
            "sustainability_score": comp_scores.get("water", 80.0),
            "explanations": explanations,
        })

    # Rank products: Feasible first, then highest score
    product_evaluations.sort(key=lambda x: (x["is_feasible"], x["score"]), reverse=True)

    run.weight_profile = product_evaluations[0]["weights"] if product_evaluations else {}

    results_to_return = []

    for rank, item in enumerate(product_evaluations, 1):
        is_top = (rank == 1 and item["is_feasible"])

        res = RecommendationResult(
            run_id=run.id,
            product_id=item["product"].id,
            rank=rank,
            feasible=item["is_feasible"],
            feasibility_notes=item["feas_reasons"],
            suitability_score=item["score"],
            component_scores=item["comp_scores"],
            estimated_yield_kg=item["annual_yield_kg"],
            estimated_revenue_inr=item["revenue"],
            estimated_opex_inr=item["opex"],
            estimated_profit_inr=item["profit"],
            estimated_roi_pct=item["roi_pct"],
            risk_score=item["risk_score"],
            sustainability_score=item["sustainability_score"],
            is_recommended=is_top,
            assumptions=[
                f"Estimates based on {area_sqm:.0f} m² {rp.area_type or 'outdoor'} cultivation area.",
                "Weather conditions derived from Open-Meteo local forecasts.",
                "Economic returns are non-guaranteed estimates for decision support only.",
            ]
        )
        db.session.add(res)
        db.session.flush()

        # Add feature importance entries
        for exp in item["explanations"]:
            fi = FeatureImportance(
                result_id=res.id,
                feature_name=exp["feature_name"],
                importance_value=exp["importance_value"],
                direction=exp["direction"],
                human_explanation=exp["human_explanation"],
            )
            db.session.add(fi)

        results_to_return.append(res)

    run.status = "complete"
    run.completed_at = datetime.now(timezone.utc)
    db.session.commit()

    # Generate Why This / Not That for top 3 alternatives
    top_result_dict = _serialize_result(results_to_return[0], detailed=False)
    comparisons = []
    for alt in results_to_return[1:4]:
        alt_dict = _serialize_result(alt, detailed=False)
        comp = generate_comparison_explanation(top_result_dict, alt_dict, objective_type)
        comparisons.append(comp)

    return jsonify({
        "success": True,
        "message": f"AI Recommendation completed: {top_result_dict['product_name']} is the top recommendation.",
        "data": {
            "run_id": run.id,
            "project_id": project.id,
            "objective_type": objective_type,
            "objective_display": objective_type.replace("_", " ").title(),
            "top_pick": _serialize_result(results_to_return[0], detailed=True),
            "all_results": [_serialize_result(r, detailed=True) for r in results_to_return],
            "why_this_summary": top_result_dict["assumptions"],
            "comparisons": comparisons,
        },
        "meta": {
            "model_version": "1.0.0-hybrid",
            "evaluated_at": run.completed_at.isoformat(),
            "attribution": "Weather data by Open-Meteo.com",
            "disclaimer": "All predictions, yield forecasts, and financial figures are non-binding estimates."
        }
    }), 200


@recommendation_bp.route("/project/<int:project_id>/latest", methods=["GET"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def get_latest_recommendation(project_id: int):
    """GET /api/recommendations/project/<id>/latest - Retrieve most recent recommendation"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    run = project.recommendation_runs.order_by(RecommendationRun.created_at.desc()).first()
    if not run:
        return jsonify({
            "success": True,
            "data": None,
            "message": "No recommendations have been run for this project yet"
        }), 200

    results = run.results.order_by(RecommendationResult.rank).all()
    top_pick = next((r for r in results if r.is_recommended), results[0] if results else None)

    return jsonify({
        "success": True,
        "data": {
            "run_id": run.id,
            "status": run.status,
            "objective_type": run.objective_type,
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
            "top_pick": _serialize_result(top_pick, detailed=True) if top_pick else None,
            "all_results": [_serialize_result(r, detailed=True) for r in results],
        }
    }), 200


@recommendation_bp.route("/<int:run_id>/explain/<int:product_id>", methods=["GET"])
@jwt_required()
@require_active_user
def get_product_explanation(run_id: int, product_id: int):
    """GET /api/recommendations/<run_id>/explain/<product_id> - Deep explainability for one product"""
    res = RecommendationResult.query.filter_by(run_id=run_id, product_id=product_id).first()
    if not res:
        return jsonify({"success": False, "error": "Recommendation result not found"}), 404

    return jsonify({
        "success": True,
        "data": _serialize_result(res, detailed=True)
    }), 200
