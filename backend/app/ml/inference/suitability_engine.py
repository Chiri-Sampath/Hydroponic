"""
AgriSmart AI — Suitability Engine (Layer 2)
=============================================
Calculates multi-factor suitability scores (0-100) using dynamic objective-based weights.
Evaluates 9 core dimensions:
  1. weather (climate optimality, solar radiation, temperature deviation)
  2. water (water use efficiency, recycling capability)
  3. investment (capital efficiency, capex/budget match)
  4. area (space utilization, vertical scaling potential)
  5. labor (labor intensity vs available workforce)
  6. yield (harvest frequency, kg/m² cycle yield)
  7. economics (indicative margin per kg, revenue density)
  8. nutrition (protein, micronutrient density)
  9. risk (climate sensitivity, market demand volatility)
"""

from typing import Dict, Any, Tuple

# 10 Objective Weight Profiles
OBJECTIVE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "best_use_of_area": {
        "area": 0.30, "yield": 0.25, "economics": 0.15, "weather": 0.10,
        "water": 0.05, "investment": 0.05, "labor": 0.05, "nutrition": 0.03, "risk": 0.02
    },
    "best_use_of_capital": {
        "investment": 0.30, "economics": 0.25, "yield": 0.15, "area": 0.10,
        "weather": 0.05, "water": 0.05, "labor": 0.05, "nutrition": 0.03, "risk": 0.02
    },
    "best_for_location": {
        "weather": 0.40, "risk": 0.15, "water": 0.15, "yield": 0.10,
        "economics": 0.08, "area": 0.05, "investment": 0.03, "labor": 0.02, "nutrition": 0.02
    },
    "minimum_water": {
        "water": 0.40, "weather": 0.15, "yield": 0.10, "economics": 0.10,
        "area": 0.08, "investment": 0.07, "labor": 0.05, "risk": 0.03, "nutrition": 0.02
    },
    "minimum_manpower": {
        "labor": 0.40, "risk": 0.15, "weather": 0.10, "economics": 0.10,
        "area": 0.08, "investment": 0.07, "water": 0.05, "yield": 0.03, "nutrition": 0.02
    },
    "nutritional_objective": {
        "nutrition": 0.40, "yield": 0.15, "economics": 0.10, "weather": 0.10,
        "water": 0.08, "area": 0.07, "investment": 0.05, "labor": 0.03, "risk": 0.02
    },
    "maximum_profit": {
        "economics": 0.35, "yield": 0.20, "investment": 0.15, "area": 0.10,
        "weather": 0.08, "labor": 0.05, "water": 0.03, "nutrition": 0.02, "risk": 0.02
    },
    "fastest_harvest": {
        "yield": 0.35, "economics": 0.20, "weather": 0.15, "area": 0.10,
        "investment": 0.08, "water": 0.05, "labor": 0.03, "risk": 0.02, "nutrition": 0.02
    },
    "sustainability": {
        "water": 0.25, "risk": 0.20, "weather": 0.20, "yield": 0.10,
        "economics": 0.10, "area": 0.05, "investment": 0.04, "labor": 0.03, "nutrition": 0.03
    },
    "let_ai_decide": {
        "weather": 0.20, "water": 0.15, "investment": 0.15, "area": 0.10,
        "labor": 0.10, "yield": 0.10, "economics": 0.10, "nutrition": 0.05, "risk": 0.05
    },
}


def calculate_suitability_score(
    product,
    resource_profile,
    weather_data: Dict[str, Any],
    objective_type: str = "let_ai_decide"
) -> Tuple[float, Dict[str, float], Dict[str, float]]:
    """
    Compute overall suitability score (0-100) and factor breakdowns.

    Returns:
        (overall_score, component_scores, weights_used)
    """
    weights = OBJECTIVE_WEIGHTS.get(objective_type, OBJECTIVE_WEIGHTS["let_ai_decide"])

    components: Dict[str, float] = {}

    # 1. Weather Factor (0-100)
    components["weather"] = _score_weather(product, weather_data, resource_profile)

    # 2. Water Factor (0-100)
    components["water"] = _score_water(product, resource_profile)

    # 3. Investment / Budget Factor (0-100)
    components["investment"] = _score_investment(product, resource_profile)

    # 4. Area Efficiency Factor (0-100)
    components["area"] = _score_area(product, resource_profile)

    # 5. Labor / Manpower Factor (0-100)
    components["labor"] = _score_labor(product, resource_profile)

    # 6. Yield & Cycle Speed Factor (0-100)
    components["yield"] = _score_yield(product)

    # 7. Economics & Profitability Factor (0-100)
    components["economics"] = _score_economics(product)

    # 8. Nutrition Factor (0-100)
    components["nutrition"] = _score_nutrition(product)

    # 9. Risk & Resilience Factor (0-100, higher is safer/better)
    components["risk"] = _score_risk(product, weather_data, resource_profile)

    # Weighted Sum
    total_score = sum(components[k] * weights[k] for k in weights)
    total_score = max(0.0, min(100.0, total_score))

    return round(total_score, 2), {k: round(v, 2) for k, v in components.items()}, weights


def _score_weather(product, weather_data: dict, resource_profile) -> float:
    env = product.env_requirements
    if not env:
        return 70.0

    area_type = resource_profile.area_type if resource_profile else "outdoor"
    if area_type in ("indoor", "greenhouse"):
        return 90.0  # Controlled climate is inherently weather-resilient

    current_temp = 22.0
    if weather_data and "current" in weather_data and weather_data["current"]:
        current_temp = weather_data["current"].get("temperature_c", 22.0) or 22.0

    t_opt = float(env.temp_optimum_c) if env.temp_optimum_c is not None else 22.0
    t_min = float(env.temp_min_c) if env.temp_min_c is not None else 15.0
    t_max = float(env.temp_max_c) if env.temp_max_c is not None else 30.0

    # Gaussian-like temperature penalty
    diff = abs(current_temp - t_opt)
    max_range = max(1.0, (t_max - t_min) / 2.0)
    score = max(20.0, 100.0 - (diff / max_range) * 45.0)
    return min(100.0, score)


def _score_water(product, resource_profile) -> float:
    w = product.water_requirements
    if not w:
        return 75.0

    litres = float(w.water_litres_per_kg_min) if w.water_litres_per_kg_min else 25.0
    recycling = (w.water_recycling_potential or "medium").lower()

    # Lower water consumption = higher score
    if litres <= 10.0:  # e.g. Fungi
        score = 95.0
    elif litres <= 25.0:  # e.g. leafy greens / microgreens
        score = 85.0
    elif litres <= 50.0:  # e.g. microalgae / fruiting plants
        score = 72.0
    else:
        score = 55.0

    if recycling == "high":
        score += 5.0
    return min(100.0, score)


def _score_investment(product, resource_profile) -> float:
    infra = product.infrastructure
    if not infra:
        return 75.0

    capex_sqm = float(infra.estimated_capex_inr_per_sqm_min) if infra.estimated_capex_inr_per_sqm_min else 1000.0
    capital = float(resource_profile.available_capital_inr) if (resource_profile and resource_profile.available_capital_inr) else 150000.0
    area = float(resource_profile.available_area_sqm) if (resource_profile and resource_profile.available_area_sqm) else 50.0

    est_total_capex = capex_sqm * area
    ratio = capital / max(1.0, est_total_capex)

    if ratio >= 1.5:
        return 95.0
    elif ratio >= 1.0:
        return 85.0
    elif ratio >= 0.7:
        return 70.0
    else:
        return 50.0


def _score_area(product, resource_profile) -> float:
    method = product.method.name if product.method else "hydroponics"
    # Vertical hydroponics and fungi stack extremely well in small areas
    if method == "fungi":
        return 95.0
    elif method == "hydroponics":
        if "Microgreen" in product.common_name or "Basil" in product.common_name or "Lettuce" in product.common_name:
            return 90.0
        return 80.0
    elif method == "algaculture":
        return 75.0
    return 70.0


def _score_labor(product, resource_profile) -> float:
    # Microgreens & mushrooms have short turnaround; leafy greens have low maintenance
    name = product.common_name.lower()
    if "mint" in name or "coriander" in name or "lettuce" in name:
        return 88.0
    elif "spirulina" in name:
        return 80.0
    elif "mushroom" in name:
        return 78.0
    elif "tomato" in name or "cucumber" in name or "pepper" in name:
        return 70.0  # Pruning, trellising, harvesting need more manual work
    return 80.0


def _score_yield(product) -> float:
    # Based on days to harvest and yield density
    days = product.typical_harvest_days_min or 30
    yield_kg = float(product.yield_kg_per_sqm_cycle_min) if product.yield_kg_per_sqm_cycle_min else 2.0

    # Short harvest cycle = high score
    if days <= 14:  # Microgreens, Spirulina
        return 95.0
    elif days <= 35:  # Lettuce, Spinach, Basil, Oyster Mushroom
        return 88.0
    elif days <= 60:
        return 75.0
    else:
        return 65.0


def _score_economics(product) -> float:
    ca = product.cost_assumption
    if not ca:
        return 75.0

    price = float(ca.indicative_price_inr_per_kg_min) if ca.indicative_price_inr_per_kg_min else 100.0
    # Higher value crops score higher
    if price >= 400.0:  # Spirulina, Lion's Mane, Microgreens
        return 95.0
    elif price >= 150.0:  # Shiitake, Oyster Mushroom, Herbs
        return 85.0
    elif price >= 70.0:  # Lettuce, Kale, Spinach
        return 75.0
    else:
        return 60.0


def _score_nutrition(product) -> float:
    nd = product.nutrition_data
    if not nd:
        name = product.common_name.lower()
        if "spirulina" in name or "chlorella" in name:
            return 98.0
        elif "kale" in name or "spinach" in name:
            return 90.0
        elif "mushroom" in name:
            return 85.0
        return 70.0

    protein = float(nd.protein_g) if nd.protein_g else 1.0
    vit_c = float(nd.vitamin_c_mg) if nd.vitamin_c_mg else 0.0

    if protein >= 50.0:  # Spirulina
        return 98.0
    elif protein >= 3.0 or vit_c >= 50.0:  # Kale, Mushrooms
        return 88.0
    else:
        return 75.0


def _score_risk(product, weather_data: dict, resource_profile) -> float:
    # High score = low risk
    method = product.method.name if product.method else "hydroponics"
    if method == "hydroponics":
        return 85.0
    elif method == "fungi":
        return 80.0
    elif method == "algaculture":
        return 75.0
    return 75.0
