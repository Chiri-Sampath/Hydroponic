"""
AgriSmart AI — Cultivation Knowledge Base Models
=================================================
Tables:
  cultivation_methods, products,
  environmental_requirements, water_requirements,
  nutrient_requirements, substrate_requirements,
  infrastructure, nutrition_data, cost_assumptions
"""

from datetime import datetime, timezone
from ..extensions import db


class CultivationMethod(db.Model):
    """Top-level cultivation category: Hydroponics | Algaculture | Fungi"""

    __tablename__ = "cultivation_methods"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # hydroponics / algaculture / fungi
    display_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    soil_required = db.Column(db.Boolean, default=False)           # Always False for these 3
    icon = db.Column(db.String(200), nullable=True)                # icon filename / URL
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    products = db.relationship("Product", back_populates="method", lazy="dynamic")


class Product(db.Model):
    """
    Specific cultivable product.
    e.g. Lettuce (Hydroponics), Spirulina (Algaculture), Oyster Mushroom (Fungi)
    is_active: used by admin to show/hide from recommendations
    """

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    method_id = db.Column(db.Integer, db.ForeignKey("cultivation_methods.id"), nullable=False, index=True)
    common_name = db.Column(db.String(200), nullable=False)
    scientific_name = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    typical_harvest_days_min = db.Column(db.Integer, nullable=True)
    typical_harvest_days_max = db.Column(db.Integer, nullable=True)
    yield_kg_per_sqm_cycle_min = db.Column(db.Numeric(8, 3), nullable=True)
    yield_kg_per_sqm_cycle_max = db.Column(db.Numeric(8, 3), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(500), nullable=True)
    varieties = db.Column(db.JSON, nullable=True)
    cultivation_plan = db.Column(db.JSON, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    data_version = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    method = db.relationship("CultivationMethod", back_populates="products")
    env_requirements = db.relationship("EnvironmentalRequirement", back_populates="product",
                                       uselist=False, cascade="all, delete-orphan")
    water_requirements = db.relationship("WaterRequirement", back_populates="product",
                                         uselist=False, cascade="all, delete-orphan")
    nutrient_requirements = db.relationship("NutrientRequirement", back_populates="product",
                                            uselist=False, cascade="all, delete-orphan")
    substrate_requirements = db.relationship("SubstrateRequirement", back_populates="product",
                                             uselist=False, cascade="all, delete-orphan")
    infrastructure = db.relationship("InfrastructureRequirement", back_populates="product",
                                     uselist=False, cascade="all, delete-orphan")
    nutrition_data = db.relationship("NutritionData", back_populates="product",
                                     uselist=False, cascade="all, delete-orphan")
    cost_assumption = db.relationship("CostAssumption", back_populates="product",
                                      uselist=False, cascade="all, delete-orphan")
    product_test_requirements = db.relationship("ProductTestRequirement", back_populates="product",
                                                lazy="dynamic")
    market_observations = db.relationship("MarketObservation", back_populates="product", lazy="dynamic")

    def __repr__(self):
        return f"<Product {self.common_name} [{self.method.name if self.method else '?'}]>"


class EnvironmentalRequirement(db.Model):
    """Environmental conditions required by a product."""

    __tablename__ = "environmental_requirements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    temp_min_c = db.Column(db.Numeric(5, 2), nullable=True)
    temp_max_c = db.Column(db.Numeric(5, 2), nullable=True)
    temp_optimum_c = db.Column(db.Numeric(5, 2), nullable=True)
    humidity_min_pct = db.Column(db.Numeric(5, 2), nullable=True)
    humidity_max_pct = db.Column(db.Numeric(5, 2), nullable=True)
    light_requirement = db.Column(db.String(200), nullable=True)  # high / medium / low / none
    photoperiod_hours = db.Column(db.Numeric(4, 1), nullable=True)
    co2_ppm_min = db.Column(db.Integer, nullable=True)
    co2_ppm_max = db.Column(db.Integer, nullable=True)
    ventilation_required = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="env_requirements")


class WaterRequirement(db.Model):
    """Water requirements per product."""

    __tablename__ = "water_requirements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    water_litres_per_kg_min = db.Column(db.Numeric(8, 2), nullable=True)
    water_litres_per_kg_max = db.Column(db.Numeric(8, 2), nullable=True)
    ph_min = db.Column(db.Numeric(4, 2), nullable=True)
    ph_max = db.Column(db.Numeric(4, 2), nullable=True)
    ec_min_ms_cm = db.Column(db.Numeric(6, 3), nullable=True)     # Electrical conductivity
    ec_max_ms_cm = db.Column(db.Numeric(6, 3), nullable=True)
    water_recycling_potential = db.Column(db.String(50), nullable=True)  # high / medium / low
    water_quality_notes = db.Column(db.Text, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="water_requirements")


class NutrientRequirement(db.Model):
    """
    Cultivation nutrient requirements per product.
    For plants (NPK + micros), algae (N, P, carbon), fungi (substrate/carbon/N).
    These are CULTIVATION inputs, NOT human nutrition.
    """

    __tablename__ = "nutrient_requirements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    # Macronutrients (mg/L for hydroponic solution, or general description)
    nitrogen_n = db.Column(db.String(100), nullable=True)
    phosphorus_p = db.Column(db.String(100), nullable=True)
    potassium_k = db.Column(db.String(100), nullable=True)
    calcium_ca = db.Column(db.String(100), nullable=True)
    magnesium_mg = db.Column(db.String(100), nullable=True)
    sulfur_s = db.Column(db.String(100), nullable=True)
    # Micronutrients
    iron_fe = db.Column(db.String(100), nullable=True)
    zinc_zn = db.Column(db.String(100), nullable=True)
    manganese_mn = db.Column(db.String(100), nullable=True)
    copper_cu = db.Column(db.String(100), nullable=True)
    boron_b = db.Column(db.String(100), nullable=True)
    molybdenum_mo = db.Column(db.String(100), nullable=True)
    # Algae-specific
    carbon_source = db.Column(db.String(200), nullable=True)
    trace_minerals = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="nutrient_requirements")


class SubstrateRequirement(db.Model):
    """Substrate requirements — primarily for Fungi products."""

    __tablename__ = "substrate_requirements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    primary_substrate = db.Column(db.String(300), nullable=True)   # e.g. "Paddy straw, Wheat straw"
    alternative_substrates = db.Column(db.Text, nullable=True)
    substrate_moisture_pct_min = db.Column(db.Numeric(5, 2), nullable=True)
    substrate_moisture_pct_max = db.Column(db.Numeric(5, 2), nullable=True)
    sterilization_required = db.Column(db.Boolean, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="substrate_requirements")


class InfrastructureRequirement(db.Model):
    """
    Infrastructure typically required to cultivate a product.
    Stored as structured JSON lists + key flags.
    """

    __tablename__ = "infrastructure"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    tanks_required = db.Column(db.Boolean, default=False)
    pumps_required = db.Column(db.Boolean, default=False)
    racks_required = db.Column(db.Boolean, default=False)
    lighting_required = db.Column(db.Boolean, default=False)
    climate_control_required = db.Column(db.Boolean, default=False)
    growing_media = db.Column(db.String(300), nullable=True)  # rockwool / cocopeat / etc.
    infrastructure_details = db.Column(db.JSON, nullable=True)  # additional items as list
    estimated_capex_inr_per_sqm_min = db.Column(db.Numeric(10, 2), nullable=True)
    estimated_capex_inr_per_sqm_max = db.Column(db.Numeric(10, 2), nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="infrastructure")


class NutritionData(db.Model):
    """
    Human nutritional profile of the cultivated product (per 100g fresh weight).
    SEPARATE from cultivation nutrient requirements.
    Source must be documented.
    """

    __tablename__ = "nutrition_data"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    serving_basis = db.Column(db.String(50), default="per 100g fresh weight")
    calories_kcal = db.Column(db.Numeric(7, 2), nullable=True)
    protein_g = db.Column(db.Numeric(7, 3), nullable=True)
    carbohydrates_g = db.Column(db.Numeric(7, 3), nullable=True)
    fat_g = db.Column(db.Numeric(7, 3), nullable=True)
    fiber_g = db.Column(db.Numeric(7, 3), nullable=True)
    vitamin_a_ug = db.Column(db.Numeric(8, 3), nullable=True)
    vitamin_b12_ug = db.Column(db.Numeric(8, 3), nullable=True)
    vitamin_c_mg = db.Column(db.Numeric(8, 3), nullable=True)
    vitamin_d_ug = db.Column(db.Numeric(8, 3), nullable=True)
    vitamin_e_mg = db.Column(db.Numeric(8, 3), nullable=True)
    vitamin_k_ug = db.Column(db.Numeric(8, 3), nullable=True)
    calcium_mg = db.Column(db.Numeric(8, 3), nullable=True)
    iron_mg = db.Column(db.Numeric(8, 3), nullable=True)
    magnesium_mg = db.Column(db.Numeric(8, 3), nullable=True)
    potassium_mg = db.Column(db.Numeric(8, 3), nullable=True)
    zinc_mg = db.Column(db.Numeric(8, 3), nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    data_version = db.Column(db.String(50), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="nutrition_data")


class CostAssumption(db.Model):
    """
    Admin-maintained economic assumptions per product.
    All values are estimates shown as decision support only.
    """

    __tablename__ = "cost_assumptions"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), unique=True, nullable=False)
    # OPEX per kg
    electricity_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    water_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    nutrients_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    seeds_spawn_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    substrate_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    labor_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    maintenance_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    packaging_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    transport_inr_per_kg = db.Column(db.Numeric(8, 2), nullable=True)
    # Indicative selling price
    indicative_price_inr_per_kg_min = db.Column(db.Numeric(8, 2), nullable=True)
    indicative_price_inr_per_kg_max = db.Column(db.Numeric(8, 2), nullable=True)
    assumption_notes = db.Column(db.Text, nullable=True)
    data_source = db.Column(db.String(300), nullable=True)
    valid_as_of = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="cost_assumption")
