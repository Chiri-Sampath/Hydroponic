"""
AgriSmart AI — Models Package
================================
Import all models here so SQLAlchemy can discover them during
database initialization and migration generation.
"""

from .user import Role, Permission, User, UserProfile, AuditLog, role_permissions
from .project import Project, Location, ResourceProfile, Objective
from .cultivation import (
    CultivationMethod, Product, EnvironmentalRequirement,
    WaterRequirement, NutrientRequirement, SubstrateRequirement,
    InfrastructureRequirement, NutritionData, CostAssumption,
)
from .recommendation import (
    ModelVersion, ModelMetric, RecommendationRun,
    RecommendationResult, FeatureImportance,
    YieldEstimate, Scenario, BreakEvenRun,
)
from .quality import (
    Batch, QualityTest, ProductTestRequirement,
    Laboratory, LabCapability, LabTestMapping,
    LabReport, TestResult, QualityPassport,
)
from .market import (
    Industry, EndUser, MarketObservation, SalesChannel,
    PackagingOption, LogisticsRate,
    BuyerProfile, BuyerRequirement, BuyerMatch, BuyerInquiry,
    Portfolio, RotationPlan, ProductionOrder, DigitalTwinRun,
    DataSource, SystemSetting,
)

__all__ = [
    "Role", "Permission", "User", "UserProfile", "AuditLog", "role_permissions",
    "Project", "Location", "ResourceProfile", "Objective",
    "CultivationMethod", "Product", "EnvironmentalRequirement",
    "WaterRequirement", "NutrientRequirement", "SubstrateRequirement",
    "InfrastructureRequirement", "NutritionData", "CostAssumption",
    "ModelVersion", "ModelMetric", "RecommendationRun",
    "RecommendationResult", "FeatureImportance",
    "YieldEstimate", "Scenario", "BreakEvenRun",
    "Batch", "QualityTest", "ProductTestRequirement",
    "Laboratory", "LabCapability", "LabTestMapping",
    "LabReport", "TestResult", "QualityPassport",
    "Industry", "EndUser", "MarketObservation", "SalesChannel",
    "PackagingOption", "LogisticsRate",
    "BuyerProfile", "BuyerRequirement", "BuyerMatch", "BuyerInquiry",
    "Portfolio", "RotationPlan", "ProductionOrder", "DigitalTwinRun",
    "DataSource", "SystemSetting",
]
