"""
AgriSmart AI — Project, Location, Resource & Objective Models
==============================================================
Tables: projects, locations, resource_profiles, objectives
"""

from datetime import datetime, timezone
from ..extensions import db


class Project(db.Model):
    """
    Central project record owned by a General User.
    Everything in the workflow (weather, recommendations, economics, quality, market)
    is linked to a project.
    status: active | archived | deleted
    """

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum("active", "archived", "deleted", native_enum=False),
        nullable=False,
        default="active",
        index=True,
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="projects")
    location = db.relationship("Location", back_populates="project", uselist=False, cascade="all, delete-orphan")
    resource_profile = db.relationship("ResourceProfile", back_populates="project", uselist=False, cascade="all, delete-orphan")
    objective = db.relationship("Objective", back_populates="project", uselist=False, cascade="all, delete-orphan")
    recommendation_runs = db.relationship("RecommendationRun", back_populates="project", lazy="dynamic", cascade="all, delete-orphan")
    batches = db.relationship("Batch", back_populates="project", lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.id}: {self.name} (user_id={self.user_id})>"


class Location(db.Model):
    """
    Location resolved for a project.
    Geocoding is done via OSM Nominatim.
    Weather is fetched from Open-Meteo using lat/lon.
    """

    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
    raw_input = db.Column(db.String(500), nullable=False)          # What user typed
    display_name = db.Column(db.String(500), nullable=True)        # Nominatim formatted name
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    geocoding_source = db.Column(db.String(100), default="OSM Nominatim")
    geocoded_at = db.Column(db.DateTime, nullable=True)

    # Current weather (from Open-Meteo — cached)
    current_weather = db.Column(db.JSON, nullable=True)
    forecast = db.Column(db.JSON, nullable=True)
    historical_climate = db.Column(db.JSON, nullable=True)
    weather_source = db.Column(db.String(100), default="Open-Meteo")
    weather_retrieved_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship("Project", back_populates="location")

    def __repr__(self):
        return f"<Location project_id={self.project_id} lat={self.latitude} lon={self.longitude}>"


class ResourceProfile(db.Model):
    """
    User's available resources for a project.
    area_type: indoor | outdoor | greenhouse | rooftop | hybrid
    """

    __tablename__ = "resource_profiles"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)

    # Area
    available_area_sqm = db.Column(db.Numeric(10, 2), nullable=True)
    area_type = db.Column(
        db.Enum("indoor", "outdoor", "greenhouse", "rooftop", "hybrid", native_enum=False),
        nullable=True,
    )

    # Capital
    available_capital_inr = db.Column(db.Numeric(15, 2), nullable=True)

    # Water
    water_available_litres_day = db.Column(db.Numeric(10, 2), nullable=True)
    water_constraints = db.Column(db.Text, nullable=True)  # free text

    # Manpower
    manpower_workers = db.Column(db.Integer, nullable=True)
    manpower_hours_per_day = db.Column(db.Numeric(5, 2), nullable=True)

    # Existing infrastructure (JSON array of items)
    existing_infrastructure = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship("Project", back_populates="resource_profile")


class Objective(db.Model):
    """
    User's primary cultivation objective for a project.
    objective_type maps to one of the 10 defined objectives.
    """

    OBJECTIVE_TYPES = [
        "best_use_of_area",
        "best_use_of_capital",
        "best_for_location",
        "minimum_water",
        "minimum_manpower",
        "nutritional_objective",
        "maximum_profit",
        "fastest_harvest",
        "sustainability",
        "let_ai_decide",
    ]

    __tablename__ = "objectives"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
    objective_type = db.Column(db.String(50), nullable=False)
    secondary_objective = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    project = db.relationship("Project", back_populates="objective")
