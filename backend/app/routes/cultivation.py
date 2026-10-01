"""
AgriSmart AI — Cultivation Knowledge Base Routes
==================================================
Serves master knowledge base data for:
  - 3 Cultivation Methods (Hydroponics, Algaculture, Fungi) - all soil-free
  - 18 Cultivation Products
  - Environmental, Water, Nutrient, Substrate & Infrastructure requirements
  - Human Nutrition Profiles (per 100g fresh weight)
  - Cost & Economic Assumptions
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.cultivation import (
    CultivationMethod, Product, EnvironmentalRequirement,
    WaterRequirement, NutrientRequirement, SubstrateRequirement,
    InfrastructureRequirement, NutritionData, CostAssumption
)
from ..utils.auth_decorators import require_active_user

cultivation_bp = Blueprint("cultivation", __name__)


def _product_to_dict(p: Product, detailed: bool = False) -> dict:
    data = {
        "id": p.id,
        "method_id": p.method_id,
        "method_name": p.method.name if p.method else None,
        "method_display": p.method.display_name if p.method else None,
        "common_name": p.common_name,
        "scientific_name": p.scientific_name,
        "description": p.description,
        "typical_harvest_days_min": p.typical_harvest_days_min,
        "typical_harvest_days_max": p.typical_harvest_days_max,
        "yield_kg_per_sqm_cycle_min": float(p.yield_kg_per_sqm_cycle_min) if p.yield_kg_per_sqm_cycle_min is not None else None,
        "yield_kg_per_sqm_cycle_max": float(p.yield_kg_per_sqm_cycle_max) if p.yield_kg_per_sqm_cycle_max is not None else None,
        "is_active": p.is_active,
        "image_url": p.image_url,
        "varieties": p.varieties or [],
        "cultivation_plan": p.cultivation_plan or {},
        "data_source": p.data_source,
    }

    if detailed:
        # Environmental
        if p.env_requirements:
            env = p.env_requirements
            data["environmental"] = {
                "temp_min_c": float(env.temp_min_c) if env.temp_min_c is not None else None,
                "temp_max_c": float(env.temp_max_c) if env.temp_max_c is not None else None,
                "temp_optimum_c": float(env.temp_optimum_c) if env.temp_optimum_c is not None else None,
                "humidity_min_pct": float(env.humidity_min_pct) if env.humidity_min_pct is not None else None,
                "humidity_max_pct": float(env.humidity_max_pct) if env.humidity_max_pct is not None else None,
                "light_requirement": env.light_requirement,
                "photoperiod_hours": float(env.photoperiod_hours) if env.photoperiod_hours is not None else None,
                "ventilation_required": env.ventilation_required,
                "data_source": env.data_source,
            }
        else:
            data["environmental"] = None

        # Water
        if p.water_requirements:
            w = p.water_requirements
            data["water"] = {
                "water_litres_per_kg_min": float(w.water_litres_per_kg_min) if w.water_litres_per_kg_min is not None else None,
                "water_litres_per_kg_max": float(w.water_litres_per_kg_max) if w.water_litres_per_kg_max is not None else None,
                "ph_min": float(w.ph_min) if w.ph_min is not None else None,
                "ph_max": float(w.ph_max) if w.ph_max is not None else None,
                "ec_min_ms_cm": float(w.ec_min_ms_cm) if w.ec_min_ms_cm is not None else None,
                "ec_max_ms_cm": float(w.ec_max_ms_cm) if w.ec_max_ms_cm is not None else None,
                "water_recycling_potential": w.water_recycling_potential,
                "data_source": w.data_source,
            }
        else:
            data["water"] = None

        # Nutrient Requirements (Cultivation inputs)
        if p.nutrient_requirements:
            nut = p.nutrient_requirements
            data["nutrient_inputs"] = {
                "nitrogen_n": nut.nitrogen_n,
                "phosphorus_p": nut.phosphorus_p,
                "potassium_k": nut.potassium_k,
                "calcium_ca": nut.calcium_ca,
                "magnesium_mg": nut.magnesium_mg,
                "sulfur_s": nut.sulfur_s,
                "iron_fe": nut.iron_fe,
                "zinc_zn": nut.zinc_zn,
                "carbon_source": nut.carbon_source,
                "notes": nut.notes,
            }
        else:
            data["nutrient_inputs"] = None

        # Substrate Requirements (Fungi)
        if p.substrate_requirements:
            sub = p.substrate_requirements
            data["substrate"] = {
                "primary_substrate": sub.primary_substrate,
                "alternative_substrates": sub.alternative_substrates,
                "moisture_pct_min": float(sub.substrate_moisture_pct_min) if sub.substrate_moisture_pct_min is not None else None,
                "moisture_pct_max": float(sub.substrate_moisture_pct_max) if sub.substrate_moisture_pct_max is not None else None,
                "sterilization_required": sub.sterilization_required,
                "notes": sub.notes,
            }
        else:
            data["substrate"] = None

        # Infrastructure
        if p.infrastructure:
            infra = p.infrastructure
            data["infrastructure"] = {
                "tanks_required": infra.tanks_required,
                "pumps_required": infra.pumps_required,
                "racks_required": infra.racks_required,
                "lighting_required": infra.lighting_required,
                "climate_control_required": infra.climate_control_required,
                "growing_media": infra.growing_media,
                "estimated_capex_inr_per_sqm_min": float(infra.estimated_capex_inr_per_sqm_min) if infra.estimated_capex_inr_per_sqm_min is not None else None,
                "estimated_capex_inr_per_sqm_max": float(infra.estimated_capex_inr_per_sqm_max) if infra.estimated_capex_inr_per_sqm_max is not None else None,
            }
        else:
            data["infrastructure"] = None

        # Human Nutrition Data
        if p.nutrition_data:
            nd = p.nutrition_data
            data["human_nutrition"] = {
                "serving_basis": nd.serving_basis,
                "calories_kcal": float(nd.calories_kcal) if nd.calories_kcal is not None else None,
                "protein_g": float(nd.protein_g) if nd.protein_g is not None else None,
                "carbohydrates_g": float(nd.carbohydrates_g) if nd.carbohydrates_g is not None else None,
                "fat_g": float(nd.fat_g) if nd.fat_g is not None else None,
                "fiber_g": float(nd.fiber_g) if nd.fiber_g is not None else None,
                "vitamin_c_mg": float(nd.vitamin_c_mg) if nd.vitamin_c_mg is not None else None,
                "vitamin_a_ug": float(nd.vitamin_a_ug) if nd.vitamin_a_ug is not None else None,
                "iron_mg": float(nd.iron_mg) if nd.iron_mg is not None else None,
                "calcium_mg": float(nd.calcium_mg) if nd.calcium_mg is not None else None,
            }
        else:
            data["human_nutrition"] = None

        # Cost Assumptions
        if p.cost_assumption:
            ca = p.cost_assumption
            data["cost_assumptions"] = {
                "electricity_inr_per_kg": float(ca.electricity_inr_per_kg) if ca.electricity_inr_per_kg is not None else None,
                "water_inr_per_kg": float(ca.water_inr_per_kg) if ca.water_inr_per_kg is not None else None,
                "nutrients_inr_per_kg": float(ca.nutrients_inr_per_kg) if ca.nutrients_inr_per_kg is not None else None,
                "seeds_spawn_inr_per_kg": float(ca.seeds_spawn_inr_per_kg) if ca.seeds_spawn_inr_per_kg is not None else None,
                "substrate_inr_per_kg": float(ca.substrate_inr_per_kg) if ca.substrate_inr_per_kg is not None else None,
                "labor_inr_per_kg": float(ca.labor_inr_per_kg) if ca.labor_inr_per_kg is not None else None,
                "packaging_inr_per_kg": float(ca.packaging_inr_per_kg) if ca.packaging_inr_per_kg is not None else None,
                "indicative_price_inr_per_kg_min": float(ca.indicative_price_inr_per_kg_min) if ca.indicative_price_inr_per_kg_min is not None else None,
                "indicative_price_inr_per_kg_max": float(ca.indicative_price_inr_per_kg_max) if ca.indicative_price_inr_per_kg_max is not None else None,
                "valid_as_of": ca.valid_as_of.isoformat() if ca.valid_as_of else None,
            }
        else:
            data["cost_assumptions"] = None

    return data


@cultivation_bp.route("/methods", methods=["GET"])
def list_methods():
    """GET /api/cultivation/methods - List all 3 cultivation ecosystems"""
    methods = CultivationMethod.query.all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": m.id,
                "name": m.name,
                "display_name": m.display_name,
                "description": m.description,
                "soil_required": m.soil_required,
                "icon": m.icon,
                "product_count": m.products.count(),
            }
            for m in methods
        ]
    }), 200


@cultivation_bp.route("/products", methods=["GET"])
def list_products():
    """
    GET /api/cultivation/products?method_id=1&active_only=true
    List cultivable products with optional method filtering.
    """
    query = Product.query
    method_id = request.args.get("method_id")
    if method_id and method_id.strip() and method_id.strip().isdigit():
        query = query.filter_by(method_id=int(method_id.strip()))

    active_only = request.args.get("active_only", "true").lower() == "true"
    if active_only:
        query = query.filter_by(is_active=True)

    products = query.order_by(Product.common_name).all()
    return jsonify({
        "success": True,
        "data": [_product_to_dict(p, detailed=False) for p in products],
        "meta": {"count": len(products)}
    }), 200


@cultivation_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    """GET /api/cultivation/products/<id> - Full product detail & agronomic requirements"""
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    return jsonify({
        "success": True,
        "data": _product_to_dict(product, detailed=True)
    }), 200
