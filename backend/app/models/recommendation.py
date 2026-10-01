"""
AgriSmart AI — AI/ML Recommendation Models
============================================
Tables: recommendation_runs, recommendation_results,
        model_versions, model_metrics, feature_importance,
        yield_estimates, scenarios, break_even_runs
"""

from datetime import datetime, timezone
from ..extensions import db


class ModelVersion(db.Model):
    """Registered ML model versions. Admin manages these."""

    __tablename__ = "model_versions"

    id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String(100), nullable=False)    # e.g. 'suitability', 'yield', 'risk'
    version = db.Column(db.String(50), nullable=False)    # e.g. '1.0.0'
    algorithm = db.Column(db.String(100), nullable=True)  # e.g. 'XGBoost', 'rule_based'
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    artifact_path = db.Column(db.String(500), nullable=True)  # local path to .pkl / .joblib
    training_data_description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    metrics = db.relationship("ModelMetric", back_populates="model_version", lazy="dynamic",
                               cascade="all, delete-orphan")


class ModelMetric(db.Model):
    """Performance metrics for a registered model version."""

    __tablename__ = "model_metrics"

    id = db.Column(db.Integer, primary_key=True)
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id"), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)   # e.g. 'MAE', 'RMSE', 'F1'
    metric_value = db.Column(db.Numeric(10, 6), nullable=False)
    split = db.Column(db.String(50), nullable=True)           # 'train' / 'validation' / 'test'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    model_version = db.relationship("ModelVersion", back_populates="metrics")


class RecommendationRun(db.Model):
    """
    One AI recommendation run for a project.
    Stores the inputs and links to per-product results.
    status: pending | complete | failed
    """

    __tablename__ = "recommendation_runs"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    objective_type = db.Column(db.String(50), nullable=False)
    input_snapshot = db.Column(db.JSON, nullable=True)     # full input at run time
    weight_profile = db.Column(db.JSON, nullable=True)     # objective-adjusted weights used
    model_version_id = db.Column(db.Integer, db.ForeignKey("model_versions.id"), nullable=True)
    status = db.Column(db.Enum("pending", "complete", "failed", name="rec_run_status_enum"), default="pending")
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)

    project = db.relationship("Project", back_populates="recommendation_runs")
    results = db.relationship("RecommendationResult", back_populates="run",
                               lazy="dynamic", cascade="all, delete-orphan")


class RecommendationResult(db.Model):
    """
    Per-product result in a recommendation run.
    is_recommended: True for the top-ranked option.
    feasible: passed rule-based feasibility filter.
    """

    __tablename__ = "recommendation_results"

    id = db.Column(db.Integer, primary_key=True)
    run_id = db.Column(db.Integer, db.ForeignKey("recommendation_runs.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rank = db.Column(db.Integer, nullable=True)               # 1 = best
    feasible = db.Column(db.Boolean, nullable=True)
    feasibility_notes = db.Column(db.JSON, nullable=True)     # reasons for pass/fail
    suitability_score = db.Column(db.Numeric(5, 2), nullable=True)  # 0-100
    component_scores = db.Column(db.JSON, nullable=True)      # per-factor scores
    estimated_yield_kg = db.Column(db.Numeric(10, 3), nullable=True)
    estimated_revenue_inr = db.Column(db.Numeric(15, 2), nullable=True)
    estimated_opex_inr = db.Column(db.Numeric(15, 2), nullable=True)
    estimated_profit_inr = db.Column(db.Numeric(15, 2), nullable=True)
    estimated_roi_pct = db.Column(db.Numeric(8, 2), nullable=True)
    risk_score = db.Column(db.Numeric(5, 2), nullable=True)
    sustainability_score = db.Column(db.Numeric(5, 2), nullable=True)
    cultivate_to_market_score = db.Column(db.Numeric(5, 2), nullable=True)
    is_recommended = db.Column(db.Boolean, default=False)
    assumptions = db.Column(db.JSON, nullable=True)           # list of assumption strings
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    run = db.relationship("RecommendationRun", back_populates="results")
    product = db.relationship("Product")
    feature_importance = db.relationship("FeatureImportance", back_populates="result",
                                          lazy="dynamic", cascade="all, delete-orphan")


class FeatureImportance(db.Model):
    """
    Per-feature SHAP values or rule contribution for a recommendation result.
    Used for 'Why This / Not That' explanation.
    """

    __tablename__ = "feature_importance"

    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey("recommendation_results.id"), nullable=False, index=True)
    feature_name = db.Column(db.String(200), nullable=False)
    importance_value = db.Column(db.Numeric(10, 6), nullable=True)  # SHAP value or weight contribution
    direction = db.Column(db.Enum("positive", "negative", "neutral", name="feature_direction_enum"), nullable=True)
    human_explanation = db.Column(db.Text, nullable=True)    # plain-English reason
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    result = db.relationship("RecommendationResult", back_populates="feature_importance")


class YieldEstimate(db.Model):
    """Project-level yield estimate (linked to a recommendation result)."""

    __tablename__ = "yield_estimates"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    area_sqm = db.Column(db.Numeric(10, 2), nullable=True)
    yield_kg_per_sqm = db.Column(db.Numeric(8, 3), nullable=True)
    total_yield_kg = db.Column(db.Numeric(10, 3), nullable=True)
    cycles_per_year = db.Column(db.Numeric(5, 2), nullable=True)
    annual_yield_kg = db.Column(db.Numeric(10, 3), nullable=True)
    assumptions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Scenario(db.Model):
    """
    Economics scenario — base case, what-if runs, portfolio components.
    scenario_type: base | what_if | portfolio
    """

    __tablename__ = "scenarios"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    scenario_type = db.Column(db.Enum("base", "what_if", "portfolio", name="scenario_type_enum"), nullable=False, default="base")
    name = db.Column(db.String(200), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    area_sqm = db.Column(db.Numeric(10, 2), nullable=True)
    capital_inr = db.Column(db.Numeric(15, 2), nullable=True)
    # Overridden parameters (for what-if)
    selling_price_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    yield_kg = db.Column(db.Numeric(10, 3), nullable=True)
    electricity_inr = db.Column(db.Numeric(10, 2), nullable=True)
    labor_inr = db.Column(db.Numeric(10, 2), nullable=True)
    packaging_inr = db.Column(db.Numeric(10, 2), nullable=True)
    transport_inr = db.Column(db.Numeric(10, 2), nullable=True)
    # Computed outputs
    revenue_inr = db.Column(db.Numeric(15, 2), nullable=True)
    opex_inr = db.Column(db.Numeric(15, 2), nullable=True)
    profit_inr = db.Column(db.Numeric(15, 2), nullable=True)
    roi_pct = db.Column(db.Numeric(8, 2), nullable=True)
    net_realizable_price_inr = db.Column(db.Numeric(8, 2), nullable=True)
    assumptions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class BreakEvenRun(db.Model):
    """Break-even analysis result for a project/product combination."""

    __tablename__ = "break_even_runs"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    fixed_cost_inr = db.Column(db.Numeric(15, 2), nullable=True)
    variable_cost_per_kg_inr = db.Column(db.Numeric(8, 2), nullable=True)
    selling_price_per_kg_inr = db.Column(db.Numeric(8, 2), nullable=True)
    break_even_kg = db.Column(db.Numeric(10, 3), nullable=True)
    break_even_cycles = db.Column(db.Numeric(8, 2), nullable=True)
    break_even_months = db.Column(db.Numeric(8, 2), nullable=True)
    assumptions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
