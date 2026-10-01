"""
AgriSmart AI — Explainability Module
======================================
Provides human-understandable explanations for AI recommendations:
  - Feature contribution breakdown (SHAP-style attribution)
  - "Why This" narrative summary (key advantages for user objective & constraints)
  - "Why Not That" side-by-side contrast analysis comparing the top pick with other candidates
"""

from typing import Dict, Any, List


def generate_feature_explanations(
    product,
    component_scores: Dict[str, float],
    weights: Dict[str, float],
    objective_type: str,
    feasible: bool
) -> List[Dict[str, Any]]:
    """
    Generate feature attribution items (importance, direction, human reason)
    for a product recommendation result.
    """
    factors = [
        ("weather", "Weather & Climate Fit", 75.0,
         "Optimal temperature and climate conditions for high growth rate without intensive heating/cooling.",
         "Requires significant climate control to reach ideal temperature."),
        ("water", "Water Efficiency", 75.0,
         "Extremely low water consumption and high closed-loop recycling compatibility.",
         "Higher water footprint compared to alternative closed-loop crops."),
        ("investment", "Capital & Setup Efficiency", 75.0,
         "Excellent infrastructure cost-to-budget match with low initial equipment hurdles.",
         "Requires higher initial capex for specialized lighting, tanks or climate equipment."),
        ("area", "Area Utilization Density", 75.0,
         "High vertical tier stacking capability maximizing yield per square meter.",
         "Requires more horizontal footprint, limiting total harvest volume in compact spaces."),
        ("labor", "Labor & Management Ease", 75.0,
         "Low manual labor requirements and simple maintenance cycles.",
         "Demands regular pruning, trellising, or intensive manual harvesting."),
        ("yield", "Yield & Harvest Frequency", 75.0,
         "Fast crop turnaround time enabling multiple continuous harvest cycles per year.",
         "Longer gestation period before first harvest compared to leafy greens/microgreens."),
        ("economics", "Profit Margin Potential", 75.0,
         "High market price realization and strong commercial buyer demand.",
         "Lower unit market price requires higher volume to achieve target revenue."),
        ("nutrition", "Nutritional Density", 75.0,
         "Superior protein, vitamin, and antioxidant density per 100g fresh weight.",
         "Moderate nutritional profile compared to superfood crops like Spirulina or Kale."),
        ("risk", "Operational Resilience", 75.0,
         "High biological resilience against common pests and climate fluctuations.",
         "More sensitive to sudden nutrient solution or humidity shifts."),
    ]

    explanations = []

    for key, label, baseline, pos_reason, neg_reason in factors:
        score = component_scores.get(key, 75.0)
        weight = weights.get(key, 0.10)
        delta = (score - baseline) * weight

        if score >= 80.0:
            direction = "positive"
            text = pos_reason
        elif score <= 68.0:
            direction = "negative"
            text = neg_reason
        else:
            direction = "neutral"
            text = f"Moderate {label.lower()} within standard operating expectations."

        explanations.append({
            "feature_name": label,
            "feature_key": key,
            "importance_value": round(delta, 4),
            "score": score,
            "weight": weight,
            "direction": direction,
            "human_explanation": text,
        })

    return explanations


def generate_comparison_explanation(
    top_product_result: dict,
    other_product_result: dict,
    objective_type: str
) -> dict:
    """
    Generate a direct 'Why This / Not That' contrast between the recommended product
    and an alternative product.
    """
    top_p = top_product_result["product_name"]
    other_p = other_product_result["product_name"]

    top_score = top_product_result.get("suitability_score", 0)
    other_score = other_product_result.get("suitability_score", 0)

    top_comps = top_product_result.get("component_scores", {})
    other_comps = other_product_result.get("component_scores", {})

    advantages_of_top = []
    advantages_of_other = []

    labels = {
        "weather": "Climate & Temperature Fit",
        "water": "Water Efficiency",
        "investment": "Capital / Setup Fit",
        "area": "Space Utilization",
        "labor": "Labor Simplicity",
        "yield": "Harvest Turnaround",
        "economics": "Profit Margin",
        "nutrition": "Nutrient Density",
        "risk": "Risk Profile",
    }

    for k, label in labels.items():
        diff = top_comps.get(k, 0) - other_comps.get(k, 0)
        if diff >= 8.0:
            advantages_of_top.append(f"{label} (+{diff:.1f} pts)")
        elif diff <= -8.0:
            advantages_of_other.append(f"{label} (+{abs(diff):.1f} pts)")

    summary = (
        f"{top_p} was selected over {other_p} with an overall suitability score of {top_score:.1f} vs {other_score:.1f}. "
    )

    if advantages_of_top:
        summary += f"Key advantages for {top_p}: {', '.join(advantages_of_top)}. "
    if advantages_of_other:
        summary += f"Note that {other_p} performed better in: {', '.join(advantages_of_other)}, but was penalized by your '{objective_type.replace('_', ' ')}' objective weighting."

    return {
        "top_product": top_p,
        "alternative_product": other_p,
        "score_difference": round(top_score - other_score, 2),
        "top_advantages": advantages_of_top,
        "alternative_advantages": advantages_of_other,
        "summary": summary,
    }
