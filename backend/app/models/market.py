"""
AgriSmart AI — Market, Buyer & Planning Models
================================================
Tables:
  Market: market_observations, industries, end_users,
          sales_channels, packaging_options, logistics_rates
  Buyer:  buyer_profiles, buyer_requirements, buyer_matches,
          buyer_inquiries
  Planning: what_if_runs, portfolios, rotation_plans,
            production_orders, digital_twin_runs
  Governance: data_sources, data_refresh_logs, system_settings
"""

from datetime import datetime, timezone
from ..extensions import db


# ── MARKET ──────────────────────────────────────────────────────────────────

class Industry(db.Model):
    """Industry sectors that purchase cultivation products (Admin managed)."""

    __tablename__ = "industries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    end_users = db.relationship("EndUser", back_populates="industry", lazy="dynamic")


class EndUser(db.Model):
    """
    End users within an industry that buy the product.
    e.g. Spirulina -> Nutraceutical -> Supplement Manufacturer
    """

    __tablename__ = "end_users"

    id = db.Column(db.Integer, primary_key=True)
    industry_id = db.Column(db.Integer, db.ForeignKey("industries.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True, index=True)
    end_user_type = db.Column(db.String(200), nullable=False)
    end_product = db.Column(db.String(300), nullable=True)         # e.g. "Protein supplement"
    typical_quality_grade = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    industry = db.relationship("Industry", back_populates="end_users")


class MarketObservation(db.Model):
    """
    Market price observation for a product.
    MUST have source and observed_at.
    These are observations/estimates, NOT live guaranteed prices.
    """

    __tablename__ = "market_observations"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    sales_channel = db.Column(db.String(200), nullable=True)       # e.g. "Retail", "Wholesale", "Export"
    geography = db.Column(db.String(200), nullable=True)           # e.g. "Bengaluru", "Pan-India"
    price_inr_per_kg_min = db.Column(db.Numeric(8, 2), nullable=True)
    price_inr_per_kg_max = db.Column(db.Numeric(8, 2), nullable=True)
    demand_level = db.Column(db.String(50), nullable=True)         # high / medium / low
    price_trend = db.Column(db.String(50), nullable=True)          # rising / stable / falling
    data_source = db.Column(db.String(300), nullable=False)        # MANDATORY
    observed_at = db.Column(db.Date, nullable=False)               # MANDATORY
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="market_observations")


class SalesChannel(db.Model):
    """Sales channel options per product (Admin managed)."""

    __tablename__ = "sales_channels"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    channel_name = db.Column(db.String(200), nullable=False)       # e.g. "Local market", "Online"
    typical_commission_pct = db.Column(db.Numeric(5, 2), nullable=True)
    typical_spoilage_pct = db.Column(db.Numeric(5, 2), nullable=True)
    cold_chain_required = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class PackagingOption(db.Model):
    """Packaging types suitable for a product/channel (Admin managed)."""

    __tablename__ = "packaging_options"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    packaging_type = db.Column(db.String(200), nullable=False)
    unit_size_kg = db.Column(db.Numeric(6, 3), nullable=True)
    shelf_life_days = db.Column(db.Integer, nullable=True)
    cold_chain_required = db.Column(db.Boolean, default=False)
    estimated_cost_inr = db.Column(db.Numeric(8, 2), nullable=True)
    suitable_channels = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class LogisticsRate(db.Model):
    """Indicative logistics cost reference data (Admin managed)."""

    __tablename__ = "logistics_rates"

    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(100), nullable=False)               # e.g. "Road", "Rail", "Air"
    distance_km_min = db.Column(db.Integer, nullable=True)
    distance_km_max = db.Column(db.Integer, nullable=True)
    cost_inr_per_kg_min = db.Column(db.Numeric(8, 2), nullable=True)
    cost_inr_per_kg_max = db.Column(db.Numeric(8, 2), nullable=True)
    cold_chain = db.Column(db.Boolean, default=False)
    data_source = db.Column(db.String(300), nullable=True)
    valid_as_of = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ── BUYER ────────────────────────────────────────────────────────────────────

class BuyerProfile(db.Model):
    """Business profile for a Buyer-role user."""

    __tablename__ = "buyer_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(300), nullable=True)
    business_type = db.Column(db.String(200), nullable=True)       # e.g. "Manufacturer", "Retailer"
    gstin = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    collection_radius_km = db.Column(db.Integer, nullable=True)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="buyer_profile")
    requirements = db.relationship("BuyerRequirement", back_populates="buyer_profile",
                                    lazy="dynamic", cascade="all, delete-orphan")


class BuyerRequirement(db.Model):
    """
    A buyer's specific product requirement.
    One buyer may have multiple requirements for different products.
    """

    __tablename__ = "buyer_requirements"

    id = db.Column(db.Integer, primary_key=True)
    buyer_profile_id = db.Column(db.Integer, db.ForeignKey("buyer_profiles.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    required_quantity_kg_per_week = db.Column(db.Numeric(10, 3), nullable=True)
    required_quantity_kg_per_month = db.Column(db.Numeric(10, 3), nullable=True)
    quality_grade = db.Column(db.String(100), nullable=True)
    required_tests = db.Column(db.JSON, nullable=True)             # list of quality_test ids
    min_price_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    target_price_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    packaging_requirements = db.Column(db.Text, nullable=True)
    delivery_requirements = db.Column(db.Text, nullable=True)
    cold_chain_required = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    buyer_profile = db.relationship("BuyerProfile", back_populates="requirements")
    matches = db.relationship("BuyerMatch", back_populates="buyer_requirement", lazy="dynamic")
    inquiries = db.relationship("BuyerInquiry", back_populates="buyer_requirement", lazy="dynamic")


class BuyerMatch(db.Model):
    """Computed compatibility match between a buyer requirement and a producer project."""

    __tablename__ = "buyer_matches"

    id = db.Column(db.Integer, primary_key=True)
    buyer_requirement_id = db.Column(db.Integer, db.ForeignKey("buyer_requirements.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    compatibility_score = db.Column(db.Numeric(5, 2), nullable=True)   # 0-100
    score_breakdown = db.Column(db.JSON, nullable=True)                 # per-factor scores
    match_reasons = db.Column(db.JSON, nullable=True)                   # human-readable reasons
    computed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    buyer_requirement = db.relationship("BuyerRequirement", back_populates="matches")


class BuyerInquiry(db.Model):
    """
    Buyer inquiry to a producer.
    status: new | contacted | negotiating | accepted | rejected | closed
    """

    STATUSES = ["new", "contacted", "negotiating", "accepted", "rejected", "closed"]

    __tablename__ = "buyer_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    buyer_requirement_id = db.Column(db.Integer, db.ForeignKey("buyer_requirements.id"), nullable=False)
    producer_project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    status = db.Column(
        db.String(50),
        default="new",
        index=True,
    )
    message = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    buyer_requirement = db.relationship("BuyerRequirement", back_populates="inquiries")


# ── PLANNING ──────────────────────────────────────────────────────────────────

class Portfolio(db.Model):
    """Multi-crop portfolio optimization result for a project."""

    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    optimization_objective = db.Column(db.String(100), nullable=True)
    allocations = db.Column(db.JSON, nullable=True)    # [{product_id, area_sqm, expected_yield_kg, ...}]
    total_expected_revenue_inr = db.Column(db.Numeric(15, 2), nullable=True)
    total_expected_profit_inr = db.Column(db.Numeric(15, 2), nullable=True)
    assumptions = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class RotationPlan(db.Model):
    """12-month production rotation plan for a project."""

    __tablename__ = "rotation_plans"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    plan_year = db.Column(db.Integer, nullable=True)
    monthly_plan = db.Column(db.JSON, nullable=True)   # 12 months x allocations
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class ProductionOrder(db.Model):
    """Production-to-order plan linked to a buyer inquiry or commitment."""

    __tablename__ = "production_orders"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_inquiry_id = db.Column(db.Integer, db.ForeignKey("buyer_inquiries.id"), nullable=True)
    required_quantity_kg = db.Column(db.Numeric(10, 3), nullable=True)
    required_by_date = db.Column(db.Date, nullable=True)
    planned_start_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default="planned")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class DigitalTwinRun(db.Model):
    """
    Digital twin simulation run.
    Clearly labelled as simulation — not real production data.
    """

    __tablename__ = "digital_twin_runs"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    simulation_label = db.Column(db.String(200), default="SIMULATION — NOT REAL DATA")
    parameters = db.Column(db.JSON, nullable=True)                    # input parameter overrides
    results = db.Column(db.JSON, nullable=True)                       # projected outputs
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# ── GOVERNANCE ────────────────────────────────────────────────────────────────

class DataSource(db.Model):
    """Registry of external data sources used by the platform."""

    __tablename__ = "data_sources"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    source_type = db.Column(db.String(100), nullable=True)        # API / Manual / Dataset
    url = db.Column(db.String(500), nullable=True)
    attribution = db.Column(db.Text, nullable=True)
    license = db.Column(db.String(200), nullable=True)
    last_verified = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class SystemSetting(db.Model):
    """Key-value store for admin-configurable system settings."""

    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(200), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    updated_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
