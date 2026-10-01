"""
AgriSmart AI — Economics Service
==================================
Handles CAPEX, OPEX, Revenue, ROI, Break-Even calculations and What-If Simulations.
All calculations output clear assumption notes and non-guaranteed disclaimers.
"""

from typing import Dict, Any, List


def calculate_detailed_economics(
    product,
    area_sqm: float,
    capital_inr: float = None,
    selling_price_override: float = None,
    yield_override_kg: float = None,
    cost_overrides: dict = None
) -> Dict[str, Any]:
    """
    Calculate full financial model for a project/product.
    """
    cost_overrides = cost_overrides or {}
    ca = product.cost_assumption
    infra = product.infrastructure

    # 1. Yield Estimates
    yield_min = float(product.yield_kg_per_sqm_cycle_min or 2.0)
    yield_max = float(product.yield_kg_per_sqm_cycle_max or 4.0)
    base_yield_per_sqm = (yield_min + yield_max) / 2.0

    days = (product.typical_harvest_days_min or 30 + (product.typical_harvest_days_max or 45)) / 2.0
    cycles_per_year = max(1.0, 330.0 / max(10.0, days))

    cycle_yield_kg = (yield_override_kg if yield_override_kg is not None else (base_yield_per_sqm * area_sqm))
    annual_yield_kg = cycle_yield_kg * cycles_per_year

    # 2. CAPEX Breakdown
    capex_per_sqm_min = float(infra.estimated_capex_inr_per_sqm_min or 600.0) if infra else 600.0
    capex_per_sqm_max = float(infra.estimated_capex_inr_per_sqm_max or 1200.0) if infra else 1200.0
    base_capex_sqm = (capex_per_sqm_min + capex_per_sqm_max) / 2.0

    capex_breakdown = {
        "structure_and_racks_inr": round(base_capex_sqm * area_sqm * 0.40, 2),
        "irrigation_and_plumbing_inr": round(base_capex_sqm * area_sqm * 0.20, 2),
        "lighting_and_electrical_inr": round(base_capex_sqm * area_sqm * 0.20, 2),
        "climate_and_sensors_inr": round(base_capex_sqm * area_sqm * 0.15, 2),
        "initial_consumables_inr": round(base_capex_sqm * area_sqm * 0.05, 2),
    }
    total_capex = sum(capex_breakdown.values())

    # 3. OPEX Breakdown (per kg and annual)
    elec_per_kg = float(cost_overrides.get("electricity_inr_per_kg") or (ca.electricity_inr_per_kg if ca else 10.0) or 10.0)
    water_per_kg = float(cost_overrides.get("water_inr_per_kg") or (ca.water_inr_per_kg if ca else 3.0) or 3.0)
    nutrients_per_kg = float(cost_overrides.get("nutrients_inr_per_kg") or (ca.nutrients_inr_per_kg if ca else 8.0) or 8.0)
    seeds_per_kg = float(cost_overrides.get("seeds_spawn_inr_per_kg") or (ca.seeds_spawn_inr_per_kg if ca else 12.0) or 12.0)
    labor_per_kg = float(cost_overrides.get("labor_inr_per_kg") or (ca.labor_inr_per_kg if ca else 15.0) or 15.0)
    pkg_per_kg = float(cost_overrides.get("packaging_inr_per_kg") or (ca.packaging_inr_per_kg if ca else 6.0) or 6.0)
    maint_per_kg = float(cost_overrides.get("maintenance_inr_per_kg") or (ca.maintenance_inr_per_kg if ca else 4.0) or 4.0)

    variable_cost_per_kg = elec_per_kg + water_per_kg + nutrients_per_kg + seeds_per_kg + labor_per_kg + pkg_per_kg + maint_per_kg
    total_annual_opex = variable_cost_per_kg * annual_yield_kg

    opex_breakdown = {
        "electricity_annual_inr": round(elec_per_kg * annual_yield_kg, 2),
        "water_annual_inr": round(water_per_kg * annual_yield_kg, 2),
        "nutrients_and_media_annual_inr": round(nutrients_per_kg * annual_yield_kg, 2),
        "seeds_or_spawn_annual_inr": round(seeds_per_kg * annual_yield_kg, 2),
        "labor_annual_inr": round(labor_per_kg * annual_yield_kg, 2),
        "packaging_annual_inr": round(pkg_per_kg * annual_yield_kg, 2),
        "maintenance_annual_inr": round(maint_per_kg * annual_yield_kg, 2),
        "total_annual_opex_inr": round(total_annual_opex, 2),
        "opex_per_kg_inr": round(variable_cost_per_kg, 2),
    }

    # 4. Revenue & Margin
    default_price = float(ca.indicative_price_inr_per_kg_min if ca and ca.indicative_price_inr_per_kg_min else 120.0)
    selling_price = selling_price_override if selling_price_override is not None else default_price

    annual_revenue = annual_yield_kg * selling_price
    annual_gross_profit = max(0.0, annual_revenue - total_annual_opex)
    gross_margin_pct = (annual_gross_profit / max(1.0, annual_revenue)) * 100.0 if annual_revenue > 0 else 0.0

    # 5. ROI & Payback
    roi_pct = (annual_gross_profit / max(1.0, total_capex)) * 100.0
    payback_years = total_capex / max(1.0, annual_gross_profit) if annual_gross_profit > 0 else None

    # 6. Break-Even Analysis
    # Fixed cost = depreciation (10% of capex/yr) + maintenance buffer
    annual_fixed_cost = total_capex * 0.15
    unit_contribution_margin = max(1.0, selling_price - variable_cost_per_kg)
    break_even_kg_annual = annual_fixed_cost / unit_contribution_margin
    break_even_cycles = break_even_kg_annual / max(1.0, cycle_yield_kg)
    break_even_months = (break_even_cycles / max(0.1, cycles_per_year)) * 12.0

    return {
        "product_id": product.id,
        "product_name": product.common_name,
        "area_sqm": area_sqm,
        "harvest_days": round(days, 1),
        "cycles_per_year": round(cycles_per_year, 1),
        "cycle_yield_kg": round(cycle_yield_kg, 2),
        "annual_yield_kg": round(annual_yield_kg, 2),
        "selling_price_per_kg_inr": round(selling_price, 2),
        "total_capex_inr": round(total_capex, 2),
        "capex_breakdown": capex_breakdown,
        "opex_breakdown": opex_breakdown,
        "annual_revenue_inr": round(annual_revenue, 2),
        "annual_gross_profit_inr": round(annual_gross_profit, 2),
        "gross_margin_pct": round(gross_margin_pct, 1),
        "annual_roi_pct": round(roi_pct, 1),
        "payback_period_years": round(payback_years, 2) if payback_years else None,
        "break_even": {
            "break_even_kg_annual": round(break_even_kg_annual, 2),
            "break_even_cycles": round(break_even_cycles, 2),
            "break_even_months": round(break_even_months, 1),
            "unit_margin_inr_per_kg": round(unit_contribution_margin, 2),
        },
        "disclaimer": "All financial values are estimates based on standard industry cost parameters. Actuals vary with local utility rates, operational efficiency, and market price fluctuations."
    }
