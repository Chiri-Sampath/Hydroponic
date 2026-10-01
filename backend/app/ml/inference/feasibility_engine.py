"""
AgriSmart AI — Feasibility Engine (Layer 1)
=============================================
Evaluates hard constraints to determine if a product can physically/economically
be cultivated with the user's available resources and location conditions.
"""

from typing import Tuple, List, Dict, Any


def evaluate_feasibility(
    product,
    resource_profile,
    weather_data: Dict[str, Any]
) -> Tuple[bool, List[str], Dict[str, Any]]:
    """
    Evaluate hard constraints for a product against user resources and location weather.

    Returns:
        (is_feasible: bool, reasons: List[str], metrics: Dict[str, Any])
    """
    reasons = []
    checks = {}
    is_feasible = True

    # 1. Temperature Constraint Check
    temp_c = None
    if weather_data and "current" in weather_data and weather_data["current"]:
        temp_c = weather_data["current"].get("temperature_c")

    area_type = resource_profile.area_type if resource_profile else "outdoor"
    is_climate_controlled = area_type in ("indoor", "greenhouse")

    env = product.env_requirements
    if env and temp_c is not None and not is_climate_controlled:
        t_min = float(env.temp_min_c) if env.temp_min_c is not None else 0
        t_max = float(env.temp_max_c) if env.temp_max_c is not None else 50

        # In outdoor / rooftop environments, ambient temp must be within acceptable bounds
        if temp_c < (t_min - 4.0):
            is_feasible = False
            reasons.append(f"Current ambient temperature ({temp_c:.1f}°C) is too cold for {product.common_name} (min {t_min:.1f}°C) without indoor climate control.")
            checks["temperature"] = "FAIL_COLD"
        elif temp_c > (t_max + 4.0):
            is_feasible = False
            reasons.append(f"Current ambient temperature ({temp_c:.1f}°C) exceeds maximum limit for {product.common_name} (max {t_max:.1f}°C) without indoor cooling.")
            checks["temperature"] = "FAIL_HOT"
        else:
            checks["temperature"] = "PASS"
    else:
        checks["temperature"] = "PASS (Controlled / Tolerant)"

    # 2. Area Constraint Check
    area_sqm = float(resource_profile.available_area_sqm) if (resource_profile and resource_profile.available_area_sqm) else 50.0
    # Minimum practical footprint per method
    min_area_needed = 5.0
    if product.method and product.method.name == "algaculture":
        min_area_needed = 10.0
    elif product.method and product.method.name == "fungi":
        min_area_needed = 5.0

    if area_sqm < min_area_needed:
        is_feasible = False
        reasons.append(f"Available area ({area_sqm} m²) is below minimum commercial viable size ({min_area_needed} m²).")
        checks["area"] = "FAIL"
    else:
        checks["area"] = "PASS"

    # 3. Capital / Budget Check
    capital_inr = float(resource_profile.available_capital_inr) if (resource_profile and resource_profile.available_capital_inr) else 100000.0
    infra = product.infrastructure
    min_capex_per_sqm = float(infra.estimated_capex_inr_per_sqm_min) if (infra and infra.estimated_capex_inr_per_sqm_min) else 500.0
    total_min_capex = min_capex_per_sqm * min(area_sqm, 100.0)

    # If capital is strictly specified and is under 50% of minimum required setup
    if capital_inr < (total_min_capex * 0.4):
        is_feasible = False
        reasons.append(f"Available capital (₹{capital_inr:,.0f}) is insufficient for initial infrastructure (est. min ₹{total_min_capex:,.0f}).")
        checks["capital"] = "FAIL"
    else:
        checks["capital"] = "PASS"

    # 4. Water Availability Check
    water_available = float(resource_profile.water_available_litres_day) if (resource_profile and resource_profile.water_available_litres_day) else 500.0
    w_req = product.water_requirements
    water_per_kg = float(w_req.water_litres_per_kg_min) if (w_req and w_req.water_litres_per_kg_min) else 20.0
    # Est. daily water needed for this area
    est_daily_water = (water_per_kg * 2.0 * (area_sqm / 50.0))

    if water_available < (est_daily_water * 0.3):
        is_feasible = False
        reasons.append(f"Daily water supply ({water_available:.0f} L/day) is below estimated requirement ({est_daily_water:.0f} L/day).")
        checks["water"] = "FAIL"
    else:
        checks["water"] = "PASS"

    if is_feasible:
        reasons.append(f"Passed all hard constraint checks for {product.common_name}.")

    return is_feasible, reasons, checks
