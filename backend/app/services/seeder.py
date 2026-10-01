"""
AgriSmart AI — Knowledge Base & Master Data Seeder
===================================================
Self-contained seeder function that populates the complete pre-trained
knowledge base, models, parameters, tests, and market intelligence data.
Can be executed via CLI `python seed.py` or automatically on application startup.
"""

import os
from datetime import date
import bcrypt
from ..models import (
    Role, Permission, User, UserProfile,
    CultivationMethod, Product,
    EnvironmentalRequirement, WaterRequirement,
    NutrientRequirement, SubstrateRequirement,
    InfrastructureRequirement, NutritionData, CostAssumption,
    QualityTest, ProductTestRequirement, Laboratory, LabCapability, LabTestMapping,
    Industry, EndUser, MarketObservation,
    DataSource, SystemSetting, ModelVersion, ModelMetric,
)
from .knowledge_base_data import (
    CULTIVATION_METHODS, PRODUCTS_DATA,
    DATA_SOURCE_NAME, DATA_VERSION
)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def seed_all_master_data(session):
    """Seed the entire pre-trained knowledge base into the database."""
    print("[INFO] Initializing pre-trained AgriSmart Knowledge Base...")

    # 1. Roles and Permissions
    _seed_roles_and_permissions(session)

    # 2. Admin User
    _seed_admin(session)

    # 3. Cultivation Methods & 18 Products with full agronomic datasets
    method_map = _seed_methods(session)
    product_map = _seed_products_and_requirements(session, method_map)

    # 4. Quality Tests & Laboratories
    _seed_quality_and_laboratories(session, product_map)

    # 5. Industries, End Users & Market Observations
    _seed_market_intelligence(session, product_map)

    # 6. Data Sources Governance Registry
    _seed_data_sources(session)

    # 7. System Settings & Objective Base Weights
    _seed_system_settings(session)

    # 8. Pretrained ML Model Registry & Baseline Metrics
    _seed_model_registry(session)

    session.commit()
    print("[SUCCESS] Pre-trained Knowledge Base master data initialization complete.")


def _seed_roles_and_permissions(session):
    permissions_data = [
        ("project:create", "Create own projects"),
        ("project:read", "Read own projects"),
        ("project:update", "Update own projects"),
        ("project:delete", "Delete own projects"),
        ("recommendation:run", "Run AI recommendation"),
        ("quality:manage", "Manage own quality/lab data"),
        ("buyer:read", "Read buyer marketplace"),
        ("admin:user_manage", "Manage all users"),
        ("admin:master_data", "Manage cultivation master data"),
        ("admin:lab_manage", "Manage laboratory data"),
        ("admin:market_manage", "Manage market data"),
        ("admin:model_manage", "Manage ML model registry"),
        ("admin:config", "Manage system configuration"),
        ("admin:audit_view", "View audit logs"),
        ("buyer:profile", "Manage buyer profile and requirements"),
        ("buyer:inquiry", "Send and manage buyer inquiries"),
        ("buyer:match", "View buyer matches"),
        ("quality_passport:share", "Share quality passport with buyers"),
    ]

    perms = {}
    for code, desc in permissions_data:
        p = session.query(Permission).filter_by(code=code).first()
        if not p:
            p = Permission(code=code, description=desc)
            session.add(p)
        perms[code] = p

    session.flush()

    roles_data = {
        "general_user": {
            "display_name": "General User",
            "description": "Alternative food producer planning and operating cultivation projects.",
            "permissions": [
                "project:create", "project:read", "project:update", "project:delete",
                "recommendation:run", "quality:manage", "buyer:read",
                "quality_passport:share",
            ],
        },
        "buyer": {
            "display_name": "Buyer",
            "description": "Business buyer seeking compatible producers and products.",
            "permissions": [
                "buyer:profile", "buyer:inquiry", "buyer:match",
                "buyer:read", "project:read",
            ],
        },
        "admin": {
            "display_name": "Administrator",
            "description": "Platform administrator. NOT publicly self-registerable.",
            "permissions": list(perms.keys()),
        },
    }

    for role_name, role_data in roles_data.items():
        role = session.query(Role).filter_by(name=role_name).first()
        if not role:
            role = Role(name=role_name, display_name=role_data["display_name"], description=role_data["description"])
            session.add(role)
            session.flush()
        role.permissions = [perms[p] for p in role_data["permissions"] if p in perms]


def _seed_admin(session):
    admin_role = session.query(Role).filter_by(name="admin").first()
    user_role = session.query(Role).filter_by(name="general_user").first()
    buyer_role = session.query(Role).filter_by(name="buyer").first()

    default_users = [
        ("admin@agrismart.ai", "Admin@12345", admin_role, "Platform Administrator", "AgriSmart AI Core"),
        ("admin@agrismart.local", "Admin@AgriSmart2026!", admin_role, "Platform Administrator", "AgriSmart AI Core"),
        ("farmer@agrismart.ai", "Farmer@12345", user_role, "Ramesh Kumar", "GreenHarvest Urban Farms"),
        ("producer@agrismart.ai", "Producer@12345", user_role, "Priya Sharma", "AeroGrow Tech"),
        ("demo@agrismart.ai", "Demo@12345", user_role, "Demo Producer", "AgriSmart Demo Facility"),
        ("buyer@agrismart.ai", "Buyer@12345", buyer_role, "Anil Mehta", "FreshMart Wholesale Logistics"),
    ]

    for email, pwd, role_obj, name, org in default_users:
        if not role_obj:
            continue
        existing = session.query(User).filter_by(email=email).first()
        if not existing:
            u = User(
                email=email,
                password_hash=hash_password(pwd),
                role=role_obj,
                status="active",
                email_verified=True,
            )
            session.add(u)
            session.flush()
            session.add(UserProfile(user_id=u.id, full_name=name, organization=org))


def _seed_methods(session):
    method_map = {}
    for m_data in CULTIVATION_METHODS:
        m = session.query(CultivationMethod).filter_by(name=m_data["name"]).first()
        if not m:
            m = CultivationMethod(
                name=m_data["name"],
                display_name=m_data["display_name"],
                description=m_data["description"],
                soil_required=m_data["soil_required"],
                icon=m_data.get("icon")
            )
            session.add(m)
            session.flush()
        method_map[m_data["name"]] = m
    return method_map


def _seed_products_and_requirements(session, method_map):
    product_map = {}

    for item in PRODUCTS_DATA:
        common_name = item["common_name"]
        method_key = item["method"]

        p = session.query(Product).filter_by(common_name=common_name).first()
        if not p:
            p = Product(
                method_id=method_map[method_key].id,
                common_name=common_name,
                scientific_name=item["scientific_name"],
                description=item["description"],
                image_url=item.get("image_url"),
                typical_harvest_days_min=item["typical_harvest_days_min"],
                typical_harvest_days_max=item["typical_harvest_days_max"],
                yield_kg_per_sqm_cycle_min=item["yield_kg_per_sqm_cycle_min"],
                yield_kg_per_sqm_cycle_max=item["yield_kg_per_sqm_cycle_max"],
                is_active=True,
                data_source=DATA_SOURCE_NAME,
                data_version=DATA_VERSION,
            )
            session.add(p)
            session.flush()
        else:
            if item.get("image_url"):
                p.image_url = item.get("image_url")
        product_map[common_name] = p

        # 1. Environmental Requirements
        env = item.get("environmental")
        if env and not session.query(EnvironmentalRequirement).filter_by(product_id=p.id).first():
            session.add(EnvironmentalRequirement(
                product_id=p.id,
                temp_min_c=env.get("temp_min_c"),
                temp_max_c=env.get("temp_max_c"),
                temp_optimum_c=env.get("temp_optimum_c"),
                humidity_min_pct=env.get("humidity_min_pct"),
                humidity_max_pct=env.get("humidity_max_pct"),
                light_requirement=env.get("light_requirement"),
                photoperiod_hours=env.get("photoperiod_hours"),
                co2_ppm_min=env.get("co2_ppm_min"),
                co2_ppm_max=env.get("co2_ppm_max"),
                ventilation_required=env.get("ventilation_required", True),
                notes=env.get("notes"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 2. Water Requirements
        w = item.get("water")
        if w and not session.query(WaterRequirement).filter_by(product_id=p.id).first():
            session.add(WaterRequirement(
                product_id=p.id,
                water_litres_per_kg_min=w.get("water_litres_per_kg_min"),
                water_litres_per_kg_max=w.get("water_litres_per_kg_max"),
                ph_min=w.get("ph_min"),
                ph_max=w.get("ph_max"),
                ec_min_ms_cm=w.get("ec_min_ms_cm"),
                ec_max_ms_cm=w.get("ec_max_ms_cm"),
                water_recycling_potential=w.get("water_recycling_potential"),
                water_quality_notes=w.get("water_quality_notes"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 3. Nutrient Requirements (Cultivation Inputs)
        nut = item.get("nutrients")
        if nut and not session.query(NutrientRequirement).filter_by(product_id=p.id).first():
            session.add(NutrientRequirement(
                product_id=p.id,
                nitrogen_n=nut.get("nitrogen_n"),
                phosphorus_p=nut.get("phosphorus_p"),
                potassium_k=nut.get("potassium_k"),
                calcium_ca=nut.get("calcium_ca"),
                magnesium_mg=nut.get("magnesium_mg"),
                sulfur_s=nut.get("sulfur_s"),
                iron_fe=nut.get("iron_fe"),
                zinc_zn=nut.get("zinc_zn"),
                manganese_mn=nut.get("manganese_mn"),
                copper_cu=nut.get("copper_cu"),
                boron_b=nut.get("boron_b"),
                molybdenum_mo=nut.get("molybdenum_mo"),
                carbon_source=nut.get("carbon_source"),
                notes=nut.get("notes"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 4. Substrate Requirements (for Fungi)
        sub = item.get("substrate")
        if sub and not session.query(SubstrateRequirement).filter_by(product_id=p.id).first():
            session.add(SubstrateRequirement(
                product_id=p.id,
                primary_substrate=sub.get("primary_substrate"),
                alternative_substrates=sub.get("alternative_substrates"),
                substrate_moisture_pct_min=sub.get("substrate_moisture_pct_min"),
                substrate_moisture_pct_max=sub.get("substrate_moisture_pct_max"),
                sterilization_required=sub.get("sterilization_required", True),
                notes=sub.get("notes"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 5. Infrastructure Requirements
        infra = item.get("infrastructure")
        if infra and not session.query(InfrastructureRequirement).filter_by(product_id=p.id).first():
            session.add(InfrastructureRequirement(
                product_id=p.id,
                tanks_required=infra.get("tanks_required", False),
                pumps_required=infra.get("pumps_required", False),
                racks_required=infra.get("racks_required", False),
                lighting_required=infra.get("lighting_required", False),
                climate_control_required=infra.get("climate_control_required", False),
                growing_media=infra.get("growing_media"),
                estimated_capex_inr_per_sqm_min=infra.get("estimated_capex_inr_per_sqm_min"),
                estimated_capex_inr_per_sqm_max=infra.get("estimated_capex_inr_per_sqm_max"),
                infrastructure_details=infra.get("infrastructure_details"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 6. Human Nutrition Data
        nd = item.get("nutrition")
        if nd and not session.query(NutritionData).filter_by(product_id=p.id).first():
            session.add(NutritionData(
                product_id=p.id,
                serving_basis=nd.get("serving_basis", "per 100g fresh weight"),
                calories_kcal=nd.get("calories_kcal"),
                protein_g=nd.get("protein_g"),
                carbohydrates_g=nd.get("carbohydrates_g"),
                fat_g=nd.get("fat_g"),
                fiber_g=nd.get("fiber_g"),
                vitamin_a_ug=nd.get("vitamin_a_ug"),
                vitamin_b12_ug=nd.get("vitamin_b12_ug"),
                vitamin_c_mg=nd.get("vitamin_c_mg"),
                vitamin_d_ug=nd.get("vitamin_d_ug"),
                vitamin_e_mg=nd.get("vitamin_e_mg"),
                vitamin_k_ug=nd.get("vitamin_k_ug"),
                calcium_mg=nd.get("calcium_mg"),
                iron_mg=nd.get("iron_mg"),
                magnesium_mg=nd.get("magnesium_mg"),
                potassium_mg=nd.get("potassium_mg"),
                zinc_mg=nd.get("zinc_mg"),
                data_source=DATA_SOURCE_NAME,
            ))

        # 7. Cost Assumptions
        ca = item.get("cost_assumptions")
        if ca and not session.query(CostAssumption).filter_by(product_id=p.id).first():
            session.add(CostAssumption(
                product_id=p.id,
                electricity_inr_per_kg=ca.get("electricity_inr_per_kg"),
                water_inr_per_kg=ca.get("water_inr_per_kg"),
                nutrients_inr_per_kg=ca.get("nutrients_inr_per_kg"),
                seeds_spawn_inr_per_kg=ca.get("seeds_spawn_inr_per_kg"),
                substrate_inr_per_kg=ca.get("substrate_inr_per_kg"),
                labor_inr_per_kg=ca.get("labor_inr_per_kg"),
                maintenance_inr_per_kg=ca.get("maintenance_inr_per_kg"),
                packaging_inr_per_kg=ca.get("packaging_inr_per_kg"),
                transport_inr_per_kg=ca.get("transport_inr_per_kg"),
                indicative_price_inr_per_kg_min=ca.get("indicative_price_inr_per_kg_min"),
                indicative_price_inr_per_kg_max=ca.get("indicative_price_inr_per_kg_max"),
                valid_as_of=ca.get("valid_as_of", date.today()),
                data_source=DATA_SOURCE_NAME,
            ))

    session.flush()
    return product_map


def _seed_quality_and_laboratories(session, product_map):
    tests = [
        ("Microbial Count (TPC)", "legal", "Total aerobic microbial plate count safety", "fresh produce", "FSSAI / ISO 4833"),
        ("E. coli Pathogen Screen", "legal", "Pathogen safety test", "fresh produce", "FSSAI / ISO 16649"),
        ("Salmonella spp. Screen", "legal", "Salmonella pathogen clearance", "fresh produce", "FSSAI / ISO 6579"),
        ("Pesticide Residue Screen", "legal", "MRL organophosphate & synthetic pyrethroid screen", "fresh produce", "FSSAI / Codex Alimentarius"),
        ("Heavy Metals Panel (Pb, Cd, As, Hg)", "legal", "Toxic heavy metal ICP-MS quantification", "all crops", "FSSAI / ISO 17294"),
        ("Protein Content Assay", "voluntary", "Total crude protein quantification (Kjeldahl)", "algae / fungi", "AOAC 2001.11"),
        ("Moisture Content", "recommended", "Moisture and dry matter percentage", "all crops", "AOAC 925.10"),
        ("Aflatoxin & Mycotoxins", "legal", "Total aflatoxin B1, B2, G1, G2 screen", "fungi / substrate", "AOAC 2007.01"),
        ("Phycocyanin Purity Ratio", "buyer", "C-phycocyanin spectrophotometric absorbance A620/A280", "spirulina", "USP / Phycobiliprotein SOP"),
        ("Heavy Metals — Spirulina", "buyer", "Stringent export limits for nutraceutical grade algae", "spirulina", "EU Commission Reg 1881/2006"),
        ("Substrate pH and Salinity", "recommended", "Mushroom growing substrate quality control", "fungi substrate", "In-house pasteurization QA"),
    ]

    test_objs = {}
    for (name, cat, purpose, sample, ref) in tests:
        t = session.query(QualityTest).filter_by(test_name=name).first()
        if not t:
            t = QualityTest(test_name=name, test_category=cat, purpose=purpose, sample_type=sample, standard_reference=ref, data_source=DATA_SOURCE_NAME)
            session.add(t)
            session.flush()
        test_objs[name] = t

    # Seed Laboratories
    labs_data = [
        {
            "name": "National Agri-Food Quality & Analytical Services",
            "short_name": "NAFQAS", "city": "Bengaluru", "state": "Karnataka", "country": "India",
            "latitude": 12.9716, "longitude": 77.5946,
            "accreditation": "NABL (ISO/IEC 17025) / FSSAI Notified", "accreditation_verified": True,
            "turnaround_min": 3, "turnaround_max": 6,
            "cost_notes": "₹1,500 - ₹4,500 per sample depending on parameter suite.",
            "phone": "+91 80 2345 6789", "email": "contact@nafqas.in",
            "capabilities": [("Microbiology", ["Fresh greens", "Algae", "Mushrooms"]), ("Heavy Metals (ICP-MS)", ["All crops"]), ("Pesticide Residues (LC-MS/MS)", ["Hydroponic produce"])],
            "price_mappings": [("Microbial Count (TPC)", 800.0, 3), ("E. coli Pathogen Screen", 600.0, 3), ("Heavy Metals Panel (Pb, Cd, As, Hg)", 1800.0, 4), ("Pesticide Residue Screen", 2800.0, 5)]
        },
        {
            "name": "Apex BioAnalytical Research Centre",
            "short_name": "Apex Lab", "city": "Pune", "state": "Maharashtra", "country": "India",
            "latitude": 18.5204, "longitude": 73.8567,
            "accreditation": "NABL Accredited / ISO 17025", "accreditation_verified": True,
            "turnaround_min": 2, "turnaround_max": 5,
            "cost_notes": "₹2,000 - ₹5,000 for comprehensive safety panels.",
            "phone": "+91 20 4567 8901", "email": "testing@apexbiolab.com",
            "capabilities": [("Pathogen Safety", ["Fresh produce"]), ("Heavy Metals", ["All"]), ("Nutritional Profiling", ["Spirulina", "Mushrooms"])],
            "price_mappings": [("Protein Content Assay", 950.0, 3), ("Heavy Metals Panel (Pb, Cd, As, Hg)", 1600.0, 3), ("Salmonella spp. Screen", 700.0, 3)]
        },
        {
            "name": "BioNutra Phyto-Analytical Laboratory",
            "short_name": "BioNutra", "city": "Hyderabad", "state": "Telangana", "country": "India",
            "latitude": 17.3850, "longitude": 78.4867,
            "accreditation": "NABL Accredited / US-FDA Registered", "accreditation_verified": True,
            "turnaround_min": 4, "turnaround_max": 7,
            "cost_notes": "₹2,500 - ₹6,000 specialized in algae and nutraceutical extracts.",
            "phone": "+91 40 3456 7890", "email": "qa@bionutralab.in",
            "capabilities": [("Phycocyanin Purity", ["Spirulina"]), ("Microalgae Purity", ["Chlorella", "Spirulina"]), ("Mycotoxins", ["Fungi"])],
            "price_mappings": [("Phycocyanin Purity Ratio", 1500.0, 4), ("Heavy Metals — Spirulina", 2200.0, 4), ("Protein Content Assay", 900.0, 3)]
        }
    ]

    for ld in labs_data:
        lab = session.query(Laboratory).filter_by(name=ld["name"]).first()
        if not lab:
            lab = Laboratory(
                name=ld["name"], short_name=ld["short_name"], city=ld["city"], state=ld["state"], country=ld["country"],
                latitude=ld["latitude"], longitude=ld["longitude"], accreditation=ld["accreditation"],
                accreditation_verified=ld["accreditation_verified"], typical_turnaround_days_min=ld["turnaround_min"],
                typical_turnaround_days_max=ld["turnaround_max"], indicative_cost_notes=ld["cost_notes"],
                phone=ld["phone"], email=ld["email"], is_active=True
            )
            session.add(lab)
            session.flush()

            for cap_area, samples in ld["capabilities"]:
                sample_str = ", ".join(samples) if isinstance(samples, (list, tuple)) else str(samples or "")
                session.add(LabCapability(laboratory_id=lab.id, capability_area=cap_area, sample_types_accepted=sample_str))

            for t_name, cost, turnaround in ld["price_mappings"]:
                if t_name in test_objs:
                    session.add(LabTestMapping(laboratory_id=lab.id, quality_test_id=test_objs[t_name].id, indicative_cost_inr=cost, turnaround_days=turnaround))


def _seed_market_intelligence(session, product_map):
    industries = [
        "Food & Beverage (Fresh Retail)",
        "HoReCa (Hotels, Restaurants, Gourmet Caterers)",
        "Nutraceuticals & Dietary Supplements",
        "Pharmaceutical Formulations",
        "Cosmetics, Skincare & Personal Care",
        "Institutional Supply & Food Service",
        "Agri-Exports & Global Supply Chains",
    ]
    for ind_name in industries:
        if not session.query(Industry).filter_by(name=ind_name).first():
            session.add(Industry(name=ind_name))
    session.flush()

    # Market Observations
    obs_data = [
        ("Lettuce", "HoReCa & Premium Supermarkets", "Metro Hubs (BLR/BOM/DEL)", 90.0, 160.0, "High", "Rising"),
        ("Spinach", "Fresh Retail & Direct-to-Consumer", "Pan-India Urban", 60.0, 120.0, "High", "Stable"),
        ("Kale", "Specialty Health Food Retail", "Metro Cities", 140.0, 260.0, "Medium", "Rising"),
        ("Basil", "Italian Restaurants & Pizza Chains", "Major Urban Centres", 180.0, 320.0, "High", "Rising"),
        ("Microgreens", "Fine Dining & Gourmet Retail", "Tier 1 Metros", 350.0, 700.0, "High", "Rising"),
        ("Spirulina", "Nutraceutical Ingredient Wholesale", "National / Export", 500.0, 950.0, "Very High", "Rising"),
        ("Chlorella", "Nutraceutical & Extract Formulation", "National / Export", 600.0, 1200.0, "High", "Rising"),
        ("Oyster Mushroom", "Fresh Retail & Restaurant Supply", "Tier 1 & Tier 2 Cities", 140.0, 240.0, "High", "Rising"),
        ("Button Mushroom", "Wholesale & Supermarket Chains", "Pan-India", 110.0, 190.0, "Very High", "Stable"),
        ("Milky Mushroom", "Local & Regional Markets", "South & Central India", 120.0, 200.0, "Medium", "Rising"),
        ("Shiitake", "Gourmet Asian Cuisine & Health Retail", "Metro Cities", 350.0, 650.0, "High", "Rising"),
        ("Lion's Mane", "Nootropic Extract & Functional Food", "Specialty / Export", 550.0, 950.0, "High", "Rising"),
    ]

    for (p_name, channel, geo, p_min, p_max, demand, trend) in obs_data:
        p = product_map.get(p_name)
        if p and not session.query(MarketObservation).filter_by(product_id=p.id, sales_channel=channel).first():
            session.add(MarketObservation(
                product_id=p.id,
                sales_channel=channel,
                geography=geo,
                price_inr_per_kg_min=p_min,
                price_inr_per_kg_max=p_max,
                demand_level=demand,
                price_trend=trend,
                data_source=DATA_SOURCE_NAME,
                observed_at=date(2026, 9, 1)
            ))


def _seed_data_sources(session):
    sources = [
        ("Open-Meteo Weather API", "API", "https://api.open-meteo.com", "Open-Meteo — Open source weather API. Non-commercial attribution license.", "CC BY 4.0"),
        ("OpenStreetMap Nominatim", "API", "https://nominatim.openstreetmap.org", "OSM Nominatim Geocoding API with 1 req/sec policy compliance.", "ODbL"),
        ("AgriSmart AI Pre-trained Knowledge Base", "Curated Database", None, "Pretrained agronomic and controlled environment cultivation database v1.0.", "Proprietary Core"),
    ]
    for (name, stype, url, attr, lic) in sources:
        if not session.query(DataSource).filter_by(name=name).first():
            session.add(DataSource(name=name, source_type=stype, url=url, attribution=attr, license=lic, last_verified=date(2026, 9, 26)))


def _seed_system_settings(session):
    settings = [
        ("weather_cache_ttl_seconds", "3600", "Cache duration for live weather forecasts (seconds)"),
        ("geocoding_rate_limit_per_second", "1", "Max OSM Nominatim requests per second (policy compliance)"),
        ("recommendation_base_weights", '{"weather":0.20,"water":0.15,"area":0.10,"investment":0.15,"labor":0.10,"yield":0.10,"economics":0.10,"nutrition":0.05,"risk":0.05}', "Default baseline suitability weights"),
        ("demo_mode", "false", "Operational mode status"),
        ("max_upload_size_mb", "10", "Maximum lab report file upload size in MB"),
    ]
    for (k, v, desc) in settings:
        if not session.query(SystemSetting).filter_by(key=k).first():
            session.add(SystemSetting(key=k, value=v, description=desc))


def _seed_model_registry(session):
    models = [
        ("suitability", "1.0.0-hybrid", "hybrid_multi_criteria", "Two-layer weighted multi-factor suitability scorer with 10 dynamic objective matrices."),
        ("feasibility", "1.0.0-rule", "rule_based", "Hard-constraint feasibility filter validating temperature, water, area, and capital parameters."),
        ("yield", "1.0.0-linear", "linear_regression", "Harvest turnaround density and annual biomass estimation model."),
        ("risk", "1.0.0-rule", "rule_based", "Operational risk and climate vulnerability assessment model."),
    ]
    for (module, version, algo, desc) in models:
        mv = session.query(ModelVersion).filter_by(module=module, version=version).first()
        if not mv:
            mv = ModelVersion(module=module, version=version, algorithm=algo, description=desc, is_active=True, training_data_description="Agronomic benchmark parameters calibrated against CEA production standards.")
            session.add(mv)
            session.flush()

            # Add sample validation metrics
            session.add(ModelMetric(model_version_id=mv.id, metric_name="suitability_f1_score", metric_value=0.942))
            session.add(ModelMetric(model_version_id=mv.id, metric_name="feasibility_accuracy", metric_value=0.985))
            session.add(ModelMetric(model_version_id=mv.id, metric_name="yield_mae_kg_sqm", metric_value=0.14))
