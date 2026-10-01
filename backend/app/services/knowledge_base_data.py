"""
AgriSmart AI — Pre-trained Cultivation Knowledge Base & Master Data
===================================================================
Comprehensive agronomic, nutritional, infrastructure, financial,
quality standard, and market dataset for all 18 soil-free commercial crops:
  - 11 Hydroponics crops
  - 2 Algaculture / Microalgae species
  - 5 Fungi / Mushroom varieties

All data points are curated from agricultural research, CEA benchmarks,
FAO standards, and FSSAI food quality specifications.
"""

from datetime import date

DATA_SOURCE_NAME = "AgriSmart AI Agronomic Research Database v1.0 (ICAR / FAO / USDA CEA Standards)"
DATA_VERSION = "1.0.0-pretrained"

# ── 1. CULTIVATION METHODS ──────────────────────────────────────────────────
CULTIVATION_METHODS = [
    {
        "name": "hydroponics",
        "display_name": "Hydroponics (Soil-Free)",
        "description": "High-efficiency water and nutrient solution closed-loop cultivation. Up to 90% water conservation, zero topsoil requirement, and vertical rack scalability.",
        "soil_required": False,
        "icon": "sprout",
    },
    {
        "name": "algaculture",
        "display_name": "Algaculture / Microalgae",
        "description": "Photobioreactor and open raceway cultivation of high-protein microalgae. Exceptional carbon capture, high nutrient density, and fast 7-14 day harvest cycles.",
        "soil_required": False,
        "icon": "waves",
    },
    {
        "name": "fungi",
        "display_name": "Fungi / Mushroom Cultivation",
        "description": "Indoor climate-controlled cultivation utilizing agricultural crop residues. Zero-light requirement, high vertical space density, and rapid vegetative growth.",
        "soil_required": False,
        "icon": "box",
    },
]

# ── 2. FULL 18 CROPS DATASET ────────────────────────────────────────────────
PRODUCTS_DATA = [
    # ── HYDROPONICS (11) ─────────────────────────────────────────────────────
    {
        "method": "hydroponics",
        "common_name": "Lettuce",
        "image_url": "https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Lactuca sativa",
        "description": "Crisp leafy green cultivated via Nutrient Film Technique (NFT) or Deep Water Culture (DWC). Fast-growing with steady commercial demand.",
        "typical_harvest_days_min": 28,
        "typical_harvest_days_max": 45,
        "yield_kg_per_sqm_cycle_min": 3.5,
        "yield_kg_per_sqm_cycle_max": 5.5,
        "environmental": {
            "temp_min_c": 15.0, "temp_max_c": 24.0, "temp_optimum_c": 19.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "medium", "photoperiod_hours": 16.0,
            "co2_ppm_min": 600, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Susceptible to tipburn if calcium transport is inadequate under high heat."
        },
        "water": {
            "water_litres_per_kg_min": 15.0, "water_litres_per_kg_max": 25.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 0.8, "ec_max_ms_cm": 1.6,
            "water_recycling_potential": "high",
            "water_quality_notes": "Maintain dissolved oxygen above 6 mg/L in root zone."
        },
        "nutrients": {
            "nitrogen_n": "150-180 ppm", "phosphorus_p": "30-50 ppm", "potassium_k": "200-240 ppm",
            "calcium_ca": "150-180 ppm", "magnesium_mg": "40-50 ppm", "sulfur_s": "50-65 ppm",
            "iron_fe": "2.0-3.0 ppm (DTPA/EDDHA)", "zinc_zn": "0.1-0.2 ppm", "manganese_mn": "0.4-0.6 ppm",
            "copper_cu": "0.02-0.05 ppm", "boron_b": "0.3-0.5 ppm", "molybdenum_mo": "0.01-0.03 ppm",
            "carbon_source": "Atmospheric CO2 enrichment", "notes": "Formulated for vegetative leaf expansion without bolting."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Rockwool cubes / Oasis foam for seedling propagation",
            "estimated_capex_inr_per_sqm_min": 650.0, "estimated_capex_inr_per_sqm_max": 1200.0,
            "infrastructure_details": ["NFT PVC channels", "Submersible water pump", "LED grow light bars (optional for outdoor/greenhouse)", "Reservoir tank (500L)"]
        },
        "nutrition": {
            "calories_kcal": 15.0, "protein_g": 1.36, "carbohydrates_g": 2.87, "fat_g": 0.15, "fiber_g": 1.3,
            "vitamin_a_ug": 370.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 9.2, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.22, "vitamin_k_ug": 126.3, "calcium_mg": 36.0, "iron_mg": 0.86,
            "magnesium_mg": 13.0, "potassium_mg": 194.0, "zinc_mg": 0.18, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 8.5, "water_inr_per_kg": 2.0, "nutrients_inr_per_kg": 6.5,
            "seeds_spawn_inr_per_kg": 4.0, "substrate_inr_per_kg": 2.5, "labor_inr_per_kg": 12.0,
            "maintenance_inr_per_kg": 3.0, "packaging_inr_per_kg": 5.0, "transport_inr_per_kg": 4.0,
            "indicative_price_inr_per_kg_min": 70.0, "indicative_price_inr_per_kg_max": 140.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Spinach",
        "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Spinacia oleracea",
        "description": "Nutrient-dense leafy green rich in iron and folate, well suited for NFT and raft hydroponics.",
        "typical_harvest_days_min": 30,
        "typical_harvest_days_max": 45,
        "yield_kg_per_sqm_cycle_min": 2.8,
        "yield_kg_per_sqm_cycle_max": 4.2,
        "environmental": {
            "temp_min_c": 10.0, "temp_max_c": 22.0, "temp_optimum_c": 17.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "medium", "photoperiod_hours": 14.0,
            "co2_ppm_min": 600, "co2_ppm_max": 900, "ventilation_required": True,
            "notes": "Prefers cooler temperatures. Warm root zones can promote pythium root rot."
        },
        "water": {
            "water_litres_per_kg_min": 16.0, "water_litres_per_kg_max": 26.0,
            "ph_min": 6.0, "ph_max": 7.0, "ec_min_ms_cm": 1.6, "ec_max_ms_cm": 2.4,
            "water_recycling_potential": "high",
            "water_quality_notes": "Requires strict water sanitation and root aeration."
        },
        "nutrients": {
            "nitrogen_n": "170-200 ppm", "phosphorus_p": "40-60 ppm", "potassium_k": "220-260 ppm",
            "calcium_ca": "140-170 ppm", "magnesium_mg": "45-55 ppm", "sulfur_s": "55-70 ppm",
            "iron_fe": "3.0-4.0 ppm", "zinc_zn": "0.15-0.25 ppm", "manganese_mn": "0.5-0.7 ppm",
            "copper_cu": "0.03-0.05 ppm", "boron_b": "0.4-0.6 ppm", "molybdenum_mo": "0.02-0.04 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "High nitrogen demand for lush dark green foliage."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Rockwool plugs / Cocopeat net cups",
            "estimated_capex_inr_per_sqm_min": 650.0, "estimated_capex_inr_per_sqm_max": 1150.0,
            "infrastructure_details": ["NFT channels", "Root zone chiller (for warm climates)", "Aeration pump"]
        },
        "nutrition": {
            "calories_kcal": 23.0, "protein_g": 2.86, "carbohydrates_g": 3.63, "fat_g": 0.39, "fiber_g": 2.2,
            "vitamin_a_ug": 469.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 28.1, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 2.03, "vitamin_k_ug": 482.9, "calcium_mg": 99.0, "iron_mg": 2.71,
            "magnesium_mg": 79.0, "potassium_mg": 558.0, "zinc_mg": 0.53, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 9.0, "water_inr_per_kg": 2.2, "nutrients_inr_per_kg": 7.0,
            "seeds_spawn_inr_per_kg": 4.5, "substrate_inr_per_kg": 2.5, "labor_inr_per_kg": 12.5,
            "maintenance_inr_per_kg": 3.0, "packaging_inr_per_kg": 5.5, "transport_inr_per_kg": 4.0,
            "indicative_price_inr_per_kg_min": 80.0, "indicative_price_inr_per_kg_max": 150.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Kale",
        "image_url": "https://images.unsplash.com/photo-1524179091875-bf99a9a6af57?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Brassica oleracea var. sabellica",
        "description": "Superfood brassica with hearty ruffled leaves, commanding high premium prices in retail and health food sectors.",
        "typical_harvest_days_min": 45,
        "typical_harvest_days_max": 65,
        "yield_kg_per_sqm_cycle_min": 2.5,
        "yield_kg_per_sqm_cycle_max": 4.5,
        "environmental": {
            "temp_min_c": 10.0, "temp_max_c": 25.0, "temp_optimum_c": 18.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "medium", "photoperiod_hours": 14.0,
            "co2_ppm_min": 600, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Hardy brassica with strong resistance to mild temperature dips."
        },
        "water": {
            "water_litres_per_kg_min": 18.0, "water_litres_per_kg_max": 28.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 1.8, "ec_max_ms_cm": 2.5,
            "water_recycling_potential": "high", "water_quality_notes": "Handles moderate EC swings well."
        },
        "nutrients": {
            "nitrogen_n": "180-220 ppm", "phosphorus_p": "45-60 ppm", "potassium_k": "240-280 ppm",
            "calcium_ca": "160-200 ppm", "magnesium_mg": "50-65 ppm", "sulfur_s": "65-80 ppm",
            "iron_fe": "2.5-3.5 ppm", "zinc_zn": "0.15-0.25 ppm", "manganese_mn": "0.5-0.7 ppm",
            "copper_cu": "0.03-0.05 ppm", "boron_b": "0.4-0.6 ppm", "molybdenum_mo": "0.02-0.04 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "Requires abundant calcium to maintain thick crinkled leaves."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Rockwool / Net pots with expanded clay pebbles",
            "estimated_capex_inr_per_sqm_min": 700.0, "estimated_capex_inr_per_sqm_max": 1250.0,
            "infrastructure_details": ["Vertical NFT towers or A-frame racks", "Delivery pump", "Digital timer"]
        },
        "nutrition": {
            "calories_kcal": 35.0, "protein_g": 2.92, "carbohydrates_g": 4.42, "fat_g": 1.49, "fiber_g": 4.1,
            "vitamin_a_ug": 241.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 93.4, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.66, "vitamin_k_ug": 389.6, "calcium_mg": 254.0, "iron_mg": 1.6,
            "magnesium_mg": 33.0, "potassium_mg": 348.0, "zinc_mg": 0.44, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 9.5, "water_inr_per_kg": 2.5, "nutrients_inr_per_kg": 7.5,
            "seeds_spawn_inr_per_kg": 5.0, "substrate_inr_per_kg": 3.0, "labor_inr_per_kg": 13.0,
            "maintenance_inr_per_kg": 3.5, "packaging_inr_per_kg": 6.0, "transport_inr_per_kg": 4.5,
            "indicative_price_inr_per_kg_min": 100.0, "indicative_price_inr_per_kg_max": 220.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Basil",
        "image_url": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Ocimum basilicum",
        "description": "Aromatic culinary herb (Genovese & Sweet Italian) highly demanded by Italian restaurants, pizzerias, and gourmet supermarkets.",
        "typical_harvest_days_min": 25,
        "typical_harvest_days_max": 35,
        "yield_kg_per_sqm_cycle_min": 1.8,
        "yield_kg_per_sqm_cycle_max": 3.2,
        "environmental": {
            "temp_min_c": 18.0, "temp_max_c": 30.0, "temp_optimum_c": 24.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "high", "photoperiod_hours": 16.0,
            "co2_ppm_min": 600, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Warm season herb. High light and warmth accelerate essential oil production."
        },
        "water": {
            "water_litres_per_kg_min": 20.0, "water_litres_per_kg_max": 35.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 1.0, "ec_max_ms_cm": 1.6,
            "water_recycling_potential": "high", "water_quality_notes": "Avoid cold water in reservoir (<18°C)."
        },
        "nutrients": {
            "nitrogen_n": "140-170 ppm", "phosphorus_p": "35-45 ppm", "potassium_k": "180-220 ppm",
            "calcium_ca": "130-160 ppm", "magnesium_mg": "35-45 ppm", "sulfur_s": "45-55 ppm",
            "iron_fe": "2.0-3.0 ppm", "zinc_zn": "0.1-0.2 ppm", "manganese_mn": "0.4-0.6 ppm",
            "copper_cu": "0.02-0.04 ppm", "boron_b": "0.3-0.5 ppm", "molybdenum_mo": "0.01-0.03 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "Balanced formula prevents excessive elongation and ensures robust aroma."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Rockwool / Oasis cubes",
            "estimated_capex_inr_per_sqm_min": 600.0, "estimated_capex_inr_per_sqm_max": 1100.0,
            "infrastructure_details": ["NFT channels", "High-intensity LED arrays", "Timer controls"]
        },
        "nutrition": {
            "calories_kcal": 22.0, "protein_g": 3.15, "carbohydrates_g": 2.65, "fat_g": 0.64, "fiber_g": 1.6,
            "vitamin_a_ug": 264.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 18.0, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.8, "vitamin_k_ug": 414.8, "calcium_mg": 177.0, "iron_mg": 3.17,
            "magnesium_mg": 64.0, "potassium_mg": 295.0, "zinc_mg": 0.81, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 11.0, "water_inr_per_kg": 2.5, "nutrients_inr_per_kg": 7.0,
            "seeds_spawn_inr_per_kg": 6.0, "substrate_inr_per_kg": 2.5, "labor_inr_per_kg": 14.0,
            "maintenance_inr_per_kg": 3.5, "packaging_inr_per_kg": 7.0, "transport_inr_per_kg": 5.0,
            "indicative_price_inr_per_kg_min": 150.0, "indicative_price_inr_per_kg_max": 300.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Mint",
        "image_url": "https://images.unsplash.com/photo-1628556270448-4d4e4148e1b1?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Mentha spicata",
        "description": "Perennial fast-spreading herb cultivated for leaves, essential oils, and continuous commercial beverage/culinary cutting.",
        "typical_harvest_days_min": 30,
        "typical_harvest_days_max": 40,
        "yield_kg_per_sqm_cycle_min": 2.0,
        "yield_kg_per_sqm_cycle_max": 3.5,
        "environmental": {
            "temp_min_c": 15.0, "temp_max_c": 28.0, "temp_optimum_c": 22.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "medium", "photoperiod_hours": 14.0,
            "co2_ppm_min": 600, "co2_ppm_max": 900, "ventilation_required": True,
            "notes": "Extremely vigorous root system; requires periodic channel maintenance."
        },
        "water": {
            "water_litres_per_kg_min": 20.0, "water_litres_per_kg_max": 35.0,
            "ph_min": 5.5, "ph_max": 7.0, "ec_min_ms_cm": 1.2, "ec_max_ms_cm": 2.0,
            "water_recycling_potential": "high", "water_quality_notes": "Tolerant of slight pH fluctuations."
        },
        "nutrients": {
            "nitrogen_n": "150-180 ppm", "phosphorus_p": "40-50 ppm", "potassium_k": "200-240 ppm",
            "calcium_ca": "140-170 ppm", "magnesium_mg": "40-50 ppm", "sulfur_s": "50-60 ppm",
            "iron_fe": "2.0-3.0 ppm", "zinc_zn": "0.1-0.2 ppm", "manganese_mn": "0.4-0.6 ppm",
            "copper_cu": "0.02-0.04 ppm", "boron_b": "0.3-0.5 ppm", "molybdenum_mo": "0.01-0.03 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "Supports multiple successive stem cuttings."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Perlite / Hydroton net cups",
            "estimated_capex_inr_per_sqm_min": 550.0, "estimated_capex_inr_per_sqm_max": 1000.0,
            "infrastructure_details": ["NFT channels with wide root clearance", "Submersible pump"]
        },
        "nutrition": {
            "calories_kcal": 44.0, "protein_g": 3.29, "carbohydrates_g": 8.41, "fat_g": 0.73, "fiber_g": 6.8,
            "vitamin_a_ug": 203.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 13.3, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.0, "vitamin_k_ug": 0.0, "calcium_mg": 199.0, "iron_mg": 11.87,
            "magnesium_mg": 63.0, "potassium_mg": 458.0, "zinc_mg": 1.09, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 8.0, "water_inr_per_kg": 2.0, "nutrients_inr_per_kg": 5.5,
            "seeds_spawn_inr_per_kg": 3.0, "substrate_inr_per_kg": 2.0, "labor_inr_per_kg": 10.0,
            "maintenance_inr_per_kg": 2.5, "packaging_inr_per_kg": 4.5, "transport_inr_per_kg": 3.5,
            "indicative_price_inr_per_kg_min": 60.0, "indicative_price_inr_per_kg_max": 120.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Coriander",
        "image_url": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Coriandrum sativum",
        "description": "Essential culinary herb widely used in Indian cuisine. Continuous demand with rapid batch turnover.",
        "typical_harvest_days_min": 21,
        "typical_harvest_days_max": 35,
        "yield_kg_per_sqm_cycle_min": 1.5,
        "yield_kg_per_sqm_cycle_max": 2.5,
        "environmental": {
            "temp_min_c": 17.0, "temp_max_c": 27.0, "temp_optimum_c": 22.0,
            "humidity_min_pct": 40.0, "humidity_max_pct": 65.0,
            "light_requirement": "medium", "photoperiod_hours": 12.0,
            "co2_ppm_min": 600, "co2_ppm_max": 800, "ventilation_required": True,
            "notes": "Avoid high temperatures which induce premature flowering."
        },
        "water": {
            "water_litres_per_kg_min": 15.0, "water_litres_per_kg_max": 25.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 1.2, "ec_max_ms_cm": 1.8,
            "water_recycling_potential": "high", "water_quality_notes": "Well oxygenated water."
        },
        "nutrients": {
            "nitrogen_n": "130-160 ppm", "phosphorus_p": "30-40 ppm", "potassium_k": "170-200 ppm",
            "calcium_ca": "120-150 ppm", "magnesium_mg": "30-40 ppm", "sulfur_s": "40-50 ppm",
            "iron_fe": "2.0-2.5 ppm", "zinc_zn": "0.1-0.2 ppm", "manganese_mn": "0.4-0.5 ppm",
            "copper_cu": "0.02-0.03 ppm", "boron_b": "0.3-0.4 ppm", "molybdenum_mo": "0.01-0.02 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "Nitrogen moderate to preserve leaf aroma."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Rockwool / Cocopeat plug",
            "estimated_capex_inr_per_sqm_min": 500.0, "estimated_capex_inr_per_sqm_max": 950.0,
            "infrastructure_details": ["NFT horizontal trays", "Circulation pump"]
        },
        "nutrition": {
            "calories_kcal": 23.0, "protein_g": 2.13, "carbohydrates_g": 3.67, "fat_g": 0.52, "fiber_g": 2.8,
            "vitamin_a_ug": 337.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 27.0, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 2.5, "vitamin_k_ug": 310.0, "calcium_mg": 67.0, "iron_mg": 1.77,
            "magnesium_mg": 26.0, "potassium_mg": 521.0, "zinc_mg": 0.5, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 7.5, "water_inr_per_kg": 1.8, "nutrients_inr_per_kg": 5.0,
            "seeds_spawn_inr_per_kg": 3.5, "substrate_inr_per_kg": 2.0, "labor_inr_per_kg": 9.5,
            "maintenance_inr_per_kg": 2.0, "packaging_inr_per_kg": 4.0, "transport_inr_per_kg": 3.0,
            "indicative_price_inr_per_kg_min": 50.0, "indicative_price_inr_per_kg_max": 100.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Tomato",
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Solanum lycopersicum",
        "description": "High-yielding vine crop (Cherry / Vine varieties) grown in Bato Dutch buckets with cocopeat substrate.",
        "typical_harvest_days_min": 70,
        "typical_harvest_days_max": 90,
        "yield_kg_per_sqm_cycle_min": 10.0,
        "yield_kg_per_sqm_cycle_max": 20.0,
        "environmental": {
            "temp_min_c": 18.0, "temp_max_c": 32.0, "temp_optimum_c": 25.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 80.0,
            "light_requirement": "high", "photoperiod_hours": 16.0,
            "co2_ppm_min": 700, "co2_ppm_max": 1200, "ventilation_required": True,
            "notes": "Requires trellising and bumblebee/vibrational pollination for heavy fruit set."
        },
        "water": {
            "water_litres_per_kg_min": 40.0, "water_litres_per_kg_max": 70.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 2.5, "ec_max_ms_cm": 3.5,
            "water_recycling_potential": "medium", "water_quality_notes": "Drain-to-waste or recirculating Dutch bucket system."
        },
        "nutrients": {
            "nitrogen_n": "200-240 ppm", "phosphorus_p": "50-70 ppm", "potassium_k": "300-360 ppm",
            "calcium_ca": "180-220 ppm", "magnesium_mg": "60-80 ppm", "sulfur_s": "70-90 ppm",
            "iron_fe": "3.0-4.5 ppm", "zinc_zn": "0.2-0.3 ppm", "manganese_mn": "0.6-0.8 ppm",
            "copper_cu": "0.04-0.06 ppm", "boron_b": "0.5-0.7 ppm", "molybdenum_mo": "0.02-0.04 ppm",
            "carbon_source": "Atmospheric CO2 enrichment", "notes": "High potassium during fruiting stage for brix sweetness."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": False,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Cocopeat slabs / Perlite in Bato Dutch buckets",
            "estimated_capex_inr_per_sqm_min": 900.0, "estimated_capex_inr_per_sqm_max": 1800.0,
            "infrastructure_details": ["Bato buckets", "Drip irrigation emitters", "Trellising roller hooks", "Exhaust cooling fans"]
        },
        "nutrition": {
            "calories_kcal": 18.0, "protein_g": 0.88, "carbohydrates_g": 3.89, "fat_g": 0.2, "fiber_g": 1.2,
            "vitamin_a_ug": 42.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 13.7, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.54, "vitamin_k_ug": 7.9, "calcium_mg": 10.0, "iron_mg": 0.27,
            "magnesium_mg": 11.0, "potassium_mg": 237.0, "zinc_mg": 0.17, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 6.0, "water_inr_per_kg": 1.5, "nutrients_inr_per_kg": 4.5,
            "seeds_spawn_inr_per_kg": 2.5, "substrate_inr_per_kg": 2.0, "labor_inr_per_kg": 7.0,
            "maintenance_inr_per_kg": 2.0, "packaging_inr_per_kg": 3.5, "transport_inr_per_kg": 2.5,
            "indicative_price_inr_per_kg_min": 35.0, "indicative_price_inr_per_kg_max": 80.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Cucumber",
        "image_url": "https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Cucumis sativus",
        "description": "Parthenocarpic English/seedless cucumber with very high vegetative and fruiting biomass yield.",
        "typical_harvest_days_min": 50,
        "typical_harvest_days_max": 70,
        "yield_kg_per_sqm_cycle_min": 8.0,
        "yield_kg_per_sqm_cycle_max": 15.0,
        "environmental": {
            "temp_min_c": 20.0, "temp_max_c": 35.0, "temp_optimum_c": 28.0,
            "humidity_min_pct": 60.0, "humidity_max_pct": 80.0,
            "light_requirement": "high", "photoperiod_hours": 16.0,
            "co2_ppm_min": 700, "co2_ppm_max": 1200, "ventilation_required": True,
            "notes": "Vigorous rapid climber; requires consistent hydration and warmth."
        },
        "water": {
            "water_litres_per_kg_min": 40.0, "water_litres_per_kg_max": 70.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 2.0, "ec_max_ms_cm": 3.0,
            "water_recycling_potential": "medium", "water_quality_notes": "High water uptake rate during peak heat."
        },
        "nutrients": {
            "nitrogen_n": "190-230 ppm", "phosphorus_p": "45-65 ppm", "potassium_k": "280-340 ppm",
            "calcium_ca": "170-210 ppm", "magnesium_mg": "55-70 ppm", "sulfur_s": "65-80 ppm",
            "iron_fe": "2.5-3.5 ppm", "zinc_zn": "0.15-0.25 ppm", "manganese_mn": "0.5-0.7 ppm",
            "copper_cu": "0.03-0.05 ppm", "boron_b": "0.4-0.6 ppm", "molybdenum_mo": "0.02-0.03 ppm",
            "carbon_source": "Atmospheric CO2 enrichment", "notes": "Balanced N-K formulation supports continuous setting."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": False,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Cocopeat grow bags / Dutch buckets",
            "estimated_capex_inr_per_sqm_min": 850.0, "estimated_capex_inr_per_sqm_max": 1650.0,
            "infrastructure_details": ["Dutch buckets / Grow bags", "High-flow drip line", "Trellis wire system"]
        },
        "nutrition": {
            "calories_kcal": 15.0, "protein_g": 0.65, "carbohydrates_g": 3.63, "fat_g": 0.11, "fiber_g": 0.5,
            "vitamin_a_ug": 5.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 2.8, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.03, "vitamin_k_ug": 16.4, "calcium_mg": 16.0, "iron_mg": 0.28,
            "magnesium_mg": 13.0, "potassium_mg": 147.0, "zinc_mg": 0.2, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 5.5, "water_inr_per_kg": 1.5, "nutrients_inr_per_kg": 4.0,
            "seeds_spawn_inr_per_kg": 2.0, "substrate_inr_per_kg": 1.8, "labor_inr_per_kg": 6.5,
            "maintenance_inr_per_kg": 1.8, "packaging_inr_per_kg": 3.0, "transport_inr_per_kg": 2.5,
            "indicative_price_inr_per_kg_min": 30.0, "indicative_price_inr_per_kg_max": 70.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Bell Pepper",
        "image_url": "https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Capsicum annuum",
        "description": "Colored capsicum (Red, Yellow, Green) cultivated under protected greenhouse hydroponics for premium market pricing.",
        "typical_harvest_days_min": 70,
        "typical_harvest_days_max": 90,
        "yield_kg_per_sqm_cycle_min": 6.0,
        "yield_kg_per_sqm_cycle_max": 12.0,
        "environmental": {
            "temp_min_c": 18.0, "temp_max_c": 32.0, "temp_optimum_c": 25.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 80.0,
            "light_requirement": "high", "photoperiod_hours": 16.0,
            "co2_ppm_min": 700, "co2_ppm_max": 1100, "ventilation_required": True,
            "notes": "Sensitive to blossom end rot under irregular irrigation or calcium deficiency."
        },
        "water": {
            "water_litres_per_kg_min": 40.0, "water_litres_per_kg_max": 70.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 2.0, "ec_max_ms_cm": 3.0,
            "water_recycling_potential": "medium", "water_quality_notes": "Maintains uniform moisture."
        },
        "nutrients": {
            "nitrogen_n": "180-220 ppm", "phosphorus_p": "45-60 ppm", "potassium_k": "260-320 ppm",
            "calcium_ca": "170-200 ppm", "magnesium_mg": "50-65 ppm", "sulfur_s": "60-75 ppm",
            "iron_fe": "2.5-3.5 ppm", "zinc_zn": "0.15-0.25 ppm", "manganese_mn": "0.5-0.7 ppm",
            "copper_cu": "0.03-0.05 ppm", "boron_b": "0.4-0.6 ppm", "molybdenum_mo": "0.02-0.03 ppm",
            "carbon_source": "Atmospheric CO2 enrichment", "notes": "High calcium and boron support thick pericarp wall development."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": False,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Cocopeat grow bags / Dutch buckets",
            "estimated_capex_inr_per_sqm_min": 850.0, "estimated_capex_inr_per_sqm_max": 1700.0,
            "infrastructure_details": ["Bato buckets", "Drip irrigation system", "Trellising twine supports"]
        },
        "nutrition": {
            "calories_kcal": 31.0, "protein_g": 0.99, "carbohydrates_g": 6.03, "fat_g": 0.3, "fiber_g": 2.1,
            "vitamin_a_ug": 157.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 127.7, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 1.58, "vitamin_k_ug": 4.9, "calcium_mg": 7.0, "iron_mg": 0.43,
            "magnesium_mg": 12.0, "potassium_mg": 211.0, "zinc_mg": 0.25, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 6.5, "water_inr_per_kg": 1.6, "nutrients_inr_per_kg": 4.8,
            "seeds_spawn_inr_per_kg": 3.0, "substrate_inr_per_kg": 2.0, "labor_inr_per_kg": 8.0,
            "maintenance_inr_per_kg": 2.2, "packaging_inr_per_kg": 4.0, "transport_inr_per_kg": 3.0,
            "indicative_price_inr_per_kg_min": 60.0, "indicative_price_inr_per_kg_max": 140.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Strawberry",
        "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Fragaria x ananassa",
        "description": "High-value premium berry cultivated in vertical gutters or tabletop substrate systems with closed-loop fertigation.",
        "typical_harvest_days_min": 90,
        "typical_harvest_days_max": 120,
        "yield_kg_per_sqm_cycle_min": 2.5,
        "yield_kg_per_sqm_cycle_max": 5.0,
        "environmental": {
            "temp_min_c": 15.0, "temp_max_c": 26.0, "temp_optimum_c": 20.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 75.0,
            "light_requirement": "medium", "photoperiod_hours": 14.0,
            "co2_ppm_min": 600, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Requires cool night temperatures (12-15°C) for flower bud differentiation."
        },
        "water": {
            "water_litres_per_kg_min": 20.0, "water_litres_per_kg_max": 40.0,
            "ph_min": 5.5, "ph_max": 6.5, "ec_min_ms_cm": 1.2, "ec_max_ms_cm": 2.0,
            "water_recycling_potential": "medium", "water_quality_notes": "Low EC prevents root burn and leaf tip necrosis."
        },
        "nutrients": {
            "nitrogen_n": "120-150 ppm", "phosphorus_p": "40-50 ppm", "potassium_k": "200-260 ppm",
            "calcium_ca": "130-160 ppm", "magnesium_mg": "40-50 ppm", "sulfur_s": "45-60 ppm",
            "iron_fe": "2.0-3.0 ppm", "zinc_zn": "0.1-0.2 ppm", "manganese_mn": "0.4-0.6 ppm",
            "copper_cu": "0.02-0.04 ppm", "boron_b": "0.3-0.5 ppm", "molybdenum_mo": "0.01-0.03 ppm",
            "carbon_source": "Atmospheric CO2 enrichment", "notes": "Potassium sulfate preferred over potassium chloride."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Cocopeat & Perlite mix (70:30) in tabletop gutters",
            "estimated_capex_inr_per_sqm_min": 1100.0, "estimated_capex_inr_per_sqm_max": 2200.0,
            "infrastructure_details": ["Tabletop gutters / Vertical cascading towers", "Cooling misting nozzles", "Drip emitters"]
        },
        "nutrition": {
            "calories_kcal": 32.0, "protein_g": 0.67, "carbohydrates_g": 7.68, "fat_g": 0.3, "fiber_g": 2.0,
            "vitamin_a_ug": 1.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 58.8, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 0.29, "vitamin_k_ug": 2.2, "calcium_mg": 16.0, "iron_mg": 0.41,
            "magnesium_mg": 13.0, "potassium_mg": 153.0, "zinc_mg": 0.14, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 14.0, "water_inr_per_kg": 2.5, "nutrients_inr_per_kg": 8.0,
            "seeds_spawn_inr_per_kg": 12.0, "substrate_inr_per_kg": 4.0, "labor_inr_per_kg": 18.0,
            "maintenance_inr_per_kg": 4.5, "packaging_inr_per_kg": 10.0, "transport_inr_per_kg": 6.0,
            "indicative_price_inr_per_kg_min": 250.0, "indicative_price_inr_per_kg_max": 500.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "hydroponics",
        "common_name": "Microgreens",
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Brassica & Herb Mix",
        "description": "Immature specialty seedlings (Radish, Mustard, Sunflower, Pea shoots) harvested at 7-14 days. Ultra-high space efficiency and top gourmet margins.",
        "typical_harvest_days_min": 7,
        "typical_harvest_days_max": 14,
        "yield_kg_per_sqm_cycle_min": 1.2,
        "yield_kg_per_sqm_cycle_max": 2.8,
        "environmental": {
            "temp_min_c": 18.0, "temp_max_c": 26.0, "temp_optimum_c": 22.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 70.0,
            "light_requirement": "low", "photoperiod_hours": 12.0,
            "co2_ppm_min": 500, "co2_ppm_max": 800, "ventilation_required": True,
            "notes": "Grown in multi-tier vertical racks under standard full-spectrum T5/LED lights."
        },
        "water": {
            "water_litres_per_kg_min": 10.0, "water_litres_per_kg_max": 20.0,
            "ph_min": 6.0, "ph_max": 7.0, "ec_min_ms_cm": 0.5, "ec_max_ms_cm": 1.2,
            "water_recycling_potential": "medium", "water_quality_notes": "Clean RO or filtered water."
        },
        "nutrients": {
            "nitrogen_n": "80-120 ppm", "phosphorus_p": "20-30 ppm", "potassium_k": "100-140 ppm",
            "calcium_ca": "80-100 ppm", "magnesium_mg": "20-30 ppm", "sulfur_s": "25-35 ppm",
            "iron_fe": "1.0-1.5 ppm", "zinc_zn": "0.05-0.1 ppm", "manganese_mn": "0.2-0.3 ppm",
            "copper_cu": "0.01-0.02 ppm", "boron_b": "0.15-0.25 ppm", "molybdenum_mo": "0.005-0.01 ppm",
            "carbon_source": "Atmospheric CO2", "notes": "Seed endosperm provides initial energy; light nutrient dosing."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": True,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Jute felt / Hemp mats / Cellulose pads",
            "estimated_capex_inr_per_sqm_min": 750.0, "estimated_capex_inr_per_sqm_max": 1400.0,
            "infrastructure_details": ["5-tier vertical steel wire racks", "1020 seedling shallow trays", "LED strip lights", "Misting timer"]
        },
        "nutrition": {
            "calories_kcal": 29.0, "protein_g": 3.4, "carbohydrates_g": 4.5, "fat_g": 0.4, "fiber_g": 2.5,
            "vitamin_a_ug": 450.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 65.0, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 3.8, "vitamin_k_ug": 250.0, "calcium_mg": 85.0, "iron_mg": 2.1,
            "magnesium_mg": 40.0, "potassium_mg": 380.0, "zinc_mg": 0.6, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 15.0, "water_inr_per_kg": 2.0, "nutrients_inr_per_kg": 5.0,
            "seeds_spawn_inr_per_kg": 25.0, "substrate_inr_per_kg": 10.0, "labor_inr_per_kg": 20.0,
            "maintenance_inr_per_kg": 4.0, "packaging_inr_per_kg": 12.0, "transport_inr_per_kg": 8.0,
            "indicative_price_inr_per_kg_min": 300.0, "indicative_price_inr_per_kg_max": 650.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },

    # ── ALGACULTURE (2) ──────────────────────────────────────────────────────
    {
        "method": "algaculture",
        "common_name": "Spirulina",
        "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Arthrospira platensis",
        "description": "Blue-green filamentous cyanobacteria renowned as a global superfood. Exceptional protein density (60-70%), phycocyanin pigment, and antioxidant profile.",
        "typical_harvest_days_min": 7,
        "typical_harvest_days_max": 14,
        "yield_kg_per_sqm_cycle_min": 0.6,
        "yield_kg_per_sqm_cycle_max": 2.2,
        "environmental": {
            "temp_min_c": 25.0, "temp_max_c": 40.0, "temp_optimum_c": 35.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 80.0,
            "light_requirement": "high", "photoperiod_hours": 12.0,
            "co2_ppm_min": 800, "co2_ppm_max": 2000, "ventilation_required": False,
            "notes": "Thrives in high alkaline medium (pH 9.0-10.5) which naturally prevents weed and pathogen contamination."
        },
        "water": {
            "water_litres_per_kg_min": 30.0, "water_litres_per_kg_max": 60.0,
            "ph_min": 8.5, "ph_max": 10.5, "ec_min_ms_cm": 15.0, "ec_max_ms_cm": 35.0,
            "water_recycling_potential": "high",
            "water_quality_notes": "Medium recycled after filtration; topped up with sodium bicarbonate."
        },
        "nutrients": {
            "nitrogen_n": "Sodium nitrate / Urea buffer (2.5 g/L)", "phosphorus_p": "Dipotassium phosphate (0.5 g/L)",
            "potassium_k": "Potassium sulfate (1.0 g/L)", "calcium_ca": "Calcium chloride (0.04 g/L)",
            "magnesium_mg": "Magnesium sulfate (0.2 g/L)", "sulfur_s": "Supplied with sulfate salts",
            "iron_fe": "Ferrous sulfate EDTA (0.01 g/L)", "zinc_zn": "Trace minerals solution A5",
            "carbon_source": "Sodium bicarbonate (NaHCO3) 8-16 g/L + direct CO2 sparging",
            "notes": "Zarrouk medium formulation is the international production benchmark."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": False,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Liquid Zarrouk mineral growth medium",
            "estimated_capex_inr_per_sqm_min": 800.0, "estimated_capex_inr_per_sqm_max": 1900.0,
            "infrastructure_details": ["Raceway paddle-wheel ponds or tubular photobioreactors", "Micro-mesh harvesting screen (30-50 micron)", "Solar/hot air drying oven"]
        },
        "nutrition": {
            "calories_kcal": 290.0, "protein_g": 57.47, "carbohydrates_g": 23.9, "fat_g": 7.72, "fiber_g": 3.6,
            "vitamin_a_ug": 29.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 10.1, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 5.0, "vitamin_k_ug": 25.5, "calcium_mg": 120.0, "iron_mg": 28.5,
            "magnesium_mg": 195.0, "potassium_mg": 1363.0, "zinc_mg": 2.0, "serving_basis": "per 100g dry powder"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 25.0, "water_inr_per_kg": 5.0, "nutrients_inr_per_kg": 40.0,
            "seeds_spawn_inr_per_kg": 15.0, "substrate_inr_per_kg": 0.0, "labor_inr_per_kg": 35.0,
            "maintenance_inr_per_kg": 8.0, "packaging_inr_per_kg": 15.0, "transport_inr_per_kg": 10.0,
            "indicative_price_inr_per_kg_min": 450.0, "indicative_price_inr_per_kg_max": 900.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "algaculture",
        "common_name": "Chlorella",
        "image_url": "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Chlorella vulgaris",
        "description": "Single-celled green eukaryotic microalgae with high chlorophyll content, heavy metal detoxification properties, and valuable food supplement market.",
        "typical_harvest_days_min": 7,
        "typical_harvest_days_max": 14,
        "yield_kg_per_sqm_cycle_min": 0.4,
        "yield_kg_per_sqm_cycle_max": 1.8,
        "environmental": {
            "temp_min_c": 20.0, "temp_max_c": 35.0, "temp_optimum_c": 30.0,
            "humidity_min_pct": 50.0, "humidity_max_pct": 80.0,
            "light_requirement": "high", "photoperiod_hours": 14.0,
            "co2_ppm_min": 800, "co2_ppm_max": 2500, "ventilation_required": False,
            "notes": "Requires mechanical or ultrasonic cell wall disruption for maximum human bioavailability."
        },
        "water": {
            "water_litres_per_kg_min": 30.0, "water_litres_per_kg_max": 65.0,
            "ph_min": 6.5, "ph_max": 8.0, "ec_min_ms_cm": 2.0, "ec_max_ms_cm": 5.0,
            "water_recycling_potential": "high", "water_quality_notes": "Freshwater medium; strict sterilization."
        },
        "nutrients": {
            "nitrogen_n": "Potassium nitrate (1.2 g/L)", "phosphorus_p": "Monopotassium phosphate (0.25 g/L)",
            "potassium_k": "Supplied via phosphate & nitrate", "calcium_ca": "Calcium chloride (0.02 g/L)",
            "magnesium_mg": "Magnesium sulfate (0.25 g/L)", "sulfur_s": "Supplied via sulfates",
            "iron_fe": "EDTA-Fe complex (0.005 g/L)", "zinc_zn": "Trace element mix BG-11",
            "carbon_source": "Direct CO2 gas injection (2-5% in air stream)", "notes": "BG-11 or BBM culture medium."
        },
        "substrate": None,
        "infrastructure": {
            "tanks_required": True, "pumps_required": True, "racks_required": False,
            "lighting_required": True, "climate_control_required": False,
            "growing_media": "Liquid BG-11 mineral broth",
            "estimated_capex_inr_per_sqm_min": 950.0, "estimated_capex_inr_per_sqm_max": 2100.0,
            "infrastructure_details": ["Tubular photobioreactors", "Centrifugal continuous harvester", "Cell mill / Homogenizer", "Spray dryer"]
        },
        "nutrition": {
            "calories_kcal": 410.0, "protein_g": 58.4, "carbohydrates_g": 23.2, "fat_g": 9.3, "fiber_g": 0.3,
            "vitamin_a_ug": 51.3, "vitamin_b12_ug": 0.1, "vitamin_c_mg": 10.4, "vitamin_d_ug": 0.0,
            "vitamin_e_mg": 1.5, "vitamin_k_ug": 0.0, "calcium_mg": 221.0, "iron_mg": 130.0,
            "magnesium_mg": 315.0, "potassium_mg": 885.0, "zinc_mg": 71.0, "serving_basis": "per 100g dry powder"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 30.0, "water_inr_per_kg": 5.5, "nutrients_inr_per_kg": 45.0,
            "seeds_spawn_inr_per_kg": 20.0, "substrate_inr_per_kg": 0.0, "labor_inr_per_kg": 40.0,
            "maintenance_inr_per_kg": 10.0, "packaging_inr_per_kg": 18.0, "transport_inr_per_kg": 12.0,
            "indicative_price_inr_per_kg_min": 500.0, "indicative_price_inr_per_kg_max": 1100.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },

    # ── FUNGI / MUSHROOMS (5) ────────────────────────────────────────────────
    {
        "method": "fungi",
        "common_name": "Oyster Mushroom",
        "image_url": "https://images.unsplash.com/photo-1543362906-acfc16c67564?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Pleurotus ostreatus",
        "description": "High-yielding, fast-colonizing gourmet mushroom. Highly adaptable to various agricultural wastes (paddy straw, wheat straw, sugarcane bagasse).",
        "typical_harvest_days_min": 25,
        "typical_harvest_days_max": 35,
        "yield_kg_per_sqm_cycle_min": 1.0,
        "yield_kg_per_sqm_cycle_max": 2.0,
        "environmental": {
            "temp_min_c": 15.0, "temp_max_c": 30.0, "temp_optimum_c": 24.0,
            "humidity_min_pct": 75.0, "humidity_max_pct": 90.0,
            "light_requirement": "none", "photoperiod_hours": 0.0,
            "co2_ppm_min": 400, "co2_ppm_max": 800, "ventilation_required": True,
            "notes": "Requires complete darkness during spawn run; dim ambient light initiates fruiting pinheads."
        },
        "water": {
            "water_litres_per_kg_min": 5.0, "water_litres_per_kg_max": 10.0,
            "ph_min": 6.5, "ph_max": 7.5, "ec_min_ms_cm": None, "ec_max_ms_cm": None,
            "water_recycling_potential": "low",
            "water_quality_notes": "Used mainly for substrate hydration and ultrasonic humidification foggers."
        },
        "nutrients": {
            "nitrogen_n": "Substrate C:N ratio 30:1 to 50:1", "phosphorus_p": "Wheat bran additive (5-10%)",
            "potassium_k": "Substrate mineral ash", "calcium_ca": "Gypsum / Calcium carbonate (2% w/w)",
            "magnesium_mg": "Natural substrate content", "sulfur_s": "Supplied via gypsum (CaSO4)",
            "iron_fe": "Trace", "zinc_zn": "Trace", "carbon_source": "Lignocellulosic agro-waste (Paddy/Wheat straw)",
            "notes": "Biological efficiency of 70-100% on dry substrate weight basis."
        },
        "substrate": {
            "primary_substrate": "Paddy Straw / Wheat Straw (chopped 2-4 cm)",
            "alternative_substrates": "Sugarcane Bagasse, Cotton waste, Coconut coir dust, Banana pseudostem",
            "substrate_moisture_pct_min": 60.0, "substrate_moisture_pct_max": 70.0,
            "sterilization_required": True,
            "notes": "Hot water pasteurization (80°C for 2h) or chemical sterilization (Bavistin + Formalin) before spawning."
        },
        "infrastructure": {
            "tanks_required": False, "pumps_required": False, "racks_required": True,
            "lighting_required": False, "climate_control_required": True,
            "growing_media": "Polypropylene fruiting bags hanging on nylon ropes / shelves",
            "estimated_capex_inr_per_sqm_min": 450.0, "estimated_capex_inr_per_sqm_max": 900.0,
            "infrastructure_details": ["Dark incubation room", "Fruiting room with ultrasonic humidifier", "Exhaust fan for CO2 flushing", "Substrate boiling tank"]
        },
        "nutrition": {
            "calories_kcal": 33.0, "protein_g": 3.31, "carbohydrates_g": 6.09, "fat_g": 0.41, "fiber_g": 2.3,
            "vitamin_a_ug": 0.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 0.0, "vitamin_d_ug": 0.7,
            "vitamin_e_mg": 0.0, "vitamin_k_ug": 0.0, "calcium_mg": 3.0, "iron_mg": 1.33,
            "magnesium_mg": 18.0, "potassium_mg": 420.0, "zinc_mg": 0.77, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 6.0, "water_inr_per_kg": 1.0, "nutrients_inr_per_kg": 3.0,
            "seeds_spawn_inr_per_kg": 10.0, "substrate_inr_per_kg": 12.0, "labor_inr_per_kg": 16.0,
            "maintenance_inr_per_kg": 2.5, "packaging_inr_per_kg": 5.5, "transport_inr_per_kg": 4.0,
            "indicative_price_inr_per_kg_min": 120.0, "indicative_price_inr_per_kg_max": 220.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "fungi",
        "common_name": "Button Mushroom",
        "image_url": "https://images.unsplash.com/photo-1504544750208-dc0358e63f7f?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Agaricus bisporus",
        "description": "The most widely consumed mushroom worldwide (White Button & Cremini). Cultivated on pasteurized compost with peat casing soil.",
        "typical_harvest_days_min": 25,
        "typical_harvest_days_max": 30,
        "yield_kg_per_sqm_cycle_min": 1.2,
        "yield_kg_per_sqm_cycle_max": 2.5,
        "environmental": {
            "temp_min_c": 14.0, "temp_max_c": 22.0, "temp_optimum_c": 18.0,
            "humidity_min_pct": 80.0, "humidity_max_pct": 95.0,
            "light_requirement": "none", "photoperiod_hours": 0.0,
            "co2_ppm_min": 500, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Requires strict air temperature control (16-18°C) during cropping flush."
        },
        "water": {
            "water_litres_per_kg_min": 5.0, "water_litres_per_kg_max": 10.0,
            "ph_min": 7.0, "ph_max": 7.5, "ec_min_ms_cm": None, "ec_max_ms_cm": None,
            "water_recycling_potential": "low", "water_quality_notes": "Fine misting onto casing layer."
        },
        "nutrients": {
            "nitrogen_n": "Composted poultry manure / urea", "phosphorus_p": "Single superphosphate",
            "potassium_k": "Muriate of potash", "calcium_ca": "Gypsum (30-40 kg/tonne compost)",
            "magnesium_mg": "Compost minerals", "sulfur_s": "Supplied via gypsum",
            "carbon_source": "Fermented wheat straw / horse manure compost", "notes": "C:N ratio adjusted to 16:1 after composting."
        },
        "substrate": {
            "primary_substrate": "Synthetic Compost (Wheat straw + Chicken manure + Gypsum + Urea)",
            "alternative_substrates": "Paddy straw compost, Sugarcane trash compost",
            "substrate_moisture_pct_min": 65.0, "substrate_moisture_pct_max": 72.0,
            "sterilization_required": True,
            "notes": "Phase I outdoor composting + Phase II peak heating (60°C) and conditioning pasteurization tunnel."
        },
        "infrastructure": {
            "tanks_required": False, "pumps_required": False, "racks_required": True,
            "lighting_required": False, "climate_control_required": True,
            "growing_media": "Compost beds covered with 3-4 cm peat/coir casing soil",
            "estimated_capex_inr_per_sqm_min": 900.0, "estimated_capex_inr_per_sqm_max": 1800.0,
            "infrastructure_details": ["Insulated puff-panel growing rooms", "Air handling unit (AHU) with chilling coil", "Multi-tier aluminum shelving"]
        },
        "nutrition": {
            "calories_kcal": 22.0, "protein_g": 3.09, "carbohydrates_g": 3.26, "fat_g": 0.34, "fiber_g": 1.0,
            "vitamin_a_ug": 0.0, "vitamin_b12_ug": 0.04, "vitamin_c_mg": 2.1, "vitamin_d_ug": 0.2,
            "vitamin_e_mg": 0.01, "vitamin_k_ug": 0.0, "calcium_mg": 3.0, "iron_mg": 0.5,
            "magnesium_mg": 9.0, "potassium_mg": 318.0, "zinc_mg": 0.52, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 12.0, "water_inr_per_kg": 1.5, "nutrients_inr_per_kg": 4.0,
            "seeds_spawn_inr_per_kg": 8.0, "substrate_inr_per_kg": 18.0, "labor_inr_per_kg": 14.0,
            "maintenance_inr_per_kg": 4.0, "packaging_inr_per_kg": 5.0, "transport_inr_per_kg": 4.5,
            "indicative_price_inr_per_kg_min": 100.0, "indicative_price_inr_per_kg_max": 180.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "fungi",
        "common_name": "Milky Mushroom",
        "image_url": "https://images.unsplash.com/photo-1563245372-f21724e3856d?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Calocybe indica",
        "description": "Tropical white mushroom native to India with excellent shelf life (3-5 days at room temp) and high temperature tolerance (30-38°C).",
        "typical_harvest_days_min": 30,
        "typical_harvest_days_max": 40,
        "yield_kg_per_sqm_cycle_min": 1.0,
        "yield_kg_per_sqm_cycle_max": 2.0,
        "environmental": {
            "temp_min_c": 25.0, "temp_max_c": 38.0, "temp_optimum_c": 32.0,
            "humidity_min_pct": 75.0, "humidity_max_pct": 90.0,
            "light_requirement": "none", "photoperiod_hours": 0.0,
            "co2_ppm_min": 600, "co2_ppm_max": 1200, "ventilation_required": True,
            "notes": "Ideal for warm tropical states in India without needing expensive refrigeration."
        },
        "water": {
            "water_litres_per_kg_min": 5.0, "water_litres_per_kg_max": 10.0,
            "ph_min": 6.5, "ph_max": 7.5, "ec_min_ms_cm": None, "ec_max_ms_cm": None,
            "water_recycling_potential": "low", "water_quality_notes": "Moist casing layer kept damp."
        },
        "nutrients": {
            "nitrogen_n": "Paddy straw nitrogen", "phosphorus_p": "Trace mineral content",
            "potassium_k": "Substrate ash", "calcium_ca": "Calcium carbonate in casing (pH buffer)",
            "carbon_source": "Paddy straw / Sorghum stalks", "notes": "Casing soil (chalk + garden loam / coir pith) is mandatory for pinhead initiation."
        },
        "substrate": {
            "primary_substrate": "Paddy Straw (chopped and soaked)",
            "alternative_substrates": "Maize stalks, Cotton stalks, Wheat straw",
            "substrate_moisture_pct_min": 60.0, "substrate_moisture_pct_max": 68.0,
            "sterilization_required": True,
            "notes": "Pasteurized straw packed in cylindrical polythene bags with wheat/paddy grain spawn."
        },
        "infrastructure": {
            "tanks_required": False, "pumps_required": False, "racks_required": True,
            "lighting_required": False, "climate_control_required": False,
            "growing_media": "Straw cylinder bags with 2 cm casing layer",
            "estimated_capex_inr_per_sqm_min": 400.0, "estimated_capex_inr_per_sqm_max": 800.0,
            "infrastructure_details": ["Thatched / Polycarbonate shed", "Racks with tier supports", "Misting system"]
        },
        "nutrition": {
            "calories_kcal": 30.0, "protein_g": 3.1, "carbohydrates_g": 5.8, "fat_g": 0.35, "fiber_g": 1.8,
            "vitamin_a_ug": 0.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 1.5, "vitamin_d_ug": 0.5,
            "vitamin_e_mg": 0.0, "vitamin_k_ug": 0.0, "calcium_mg": 8.0, "iron_mg": 1.1,
            "magnesium_mg": 15.0, "potassium_mg": 390.0, "zinc_mg": 0.65, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 4.5, "water_inr_per_kg": 1.0, "nutrients_inr_per_kg": 2.5,
            "seeds_spawn_inr_per_kg": 8.0, "substrate_inr_per_kg": 10.0, "labor_inr_per_kg": 12.0,
            "maintenance_inr_per_kg": 2.0, "packaging_inr_per_kg": 4.5, "transport_inr_per_kg": 3.5,
            "indicative_price_inr_per_kg_min": 100.0, "indicative_price_inr_per_kg_max": 190.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "fungi",
        "common_name": "Shiitake",
        "image_url": "https://images.unsplash.com/photo-1518843875459-f738682238a6?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Lentinula edodes",
        "description": "Prized gourmet & medicinal mushroom rich in lentinan and umami flavor. Cultivated on supplemented hardwood sawdust blocks.",
        "typical_harvest_days_min": 60,
        "typical_harvest_days_max": 90,
        "yield_kg_per_sqm_cycle_min": 0.6,
        "yield_kg_per_sqm_cycle_max": 1.2,
        "environmental": {
            "temp_min_c": 10.0, "temp_max_c": 25.0, "temp_optimum_c": 18.0,
            "humidity_min_pct": 70.0, "humidity_max_pct": 90.0,
            "light_requirement": "low", "photoperiod_hours": 4.0,
            "co2_ppm_min": 500, "co2_ppm_max": 1000, "ventilation_required": True,
            "notes": "Requires cold-shocking (soaking in 10-12°C water for 12-24h) to trigger flush."
        },
        "water": {
            "water_litres_per_kg_min": 5.0, "water_litres_per_kg_max": 10.0,
            "ph_min": 5.5, "ph_max": 7.0, "ec_min_ms_cm": None, "ec_max_ms_cm": None,
            "water_recycling_potential": "low", "water_quality_notes": "Chilled immersion tank water."
        },
        "nutrients": {
            "nitrogen_n": "Wheat bran / Rice bran supplement (15-20%)", "phosphorus_p": "Mineral ash in wood",
            "potassium_k": "Hardwood mineral content", "calcium_ca": "Calcium carbonate / Gypsum (1%)",
            "carbon_source": "Hardwood sawdust (Oak, Beech, Maple, Rubber wood)",
            "notes": "Lignin and cellulose breakdown requires extensive vegetative browning phase (60-90 days)."
        },
        "substrate": {
            "primary_substrate": "Hardwood Sawdust (80%) + Wheat Bran (18%) + Gypsum (2%)",
            "alternative_substrates": "Hardwood logs, Corncob meal mix",
            "substrate_moisture_pct_min": 58.0, "substrate_moisture_pct_max": 64.0,
            "sterilization_required": True,
            "notes": "High-pressure autoclave sterilization (121°C at 15 psi for 2-3 hours) required."
        },
        "infrastructure": {
            "tanks_required": True, "pumps_required": False, "racks_required": True,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Autoclaved sawdust fruiting blocks in micro-filter bags",
            "estimated_capex_inr_per_sqm_min": 900.0, "estimated_capex_inr_per_sqm_max": 1900.0,
            "infrastructure_details": ["Autoclave retort", "Cleanroom laminar air flow hood", "Cold shock soaking tank", "Climate controlled fruiting room"]
        },
        "nutrition": {
            "calories_kcal": 34.0, "protein_g": 2.24, "carbohydrates_g": 6.79, "fat_g": 0.49, "fiber_g": 2.5,
            "vitamin_a_ug": 0.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 0.0, "vitamin_d_ug": 0.4,
            "vitamin_e_mg": 0.0, "vitamin_k_ug": 0.0, "calcium_mg": 2.0, "iron_mg": 0.41,
            "magnesium_mg": 20.0, "potassium_mg": 304.0, "zinc_mg": 1.03, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 18.0, "water_inr_per_kg": 2.0, "nutrients_inr_per_kg": 8.0,
            "seeds_spawn_inr_per_kg": 15.0, "substrate_inr_per_kg": 22.0, "labor_inr_per_kg": 25.0,
            "maintenance_inr_per_kg": 5.0, "packaging_inr_per_kg": 8.0, "transport_inr_per_kg": 6.0,
            "indicative_price_inr_per_kg_min": 300.0, "indicative_price_inr_per_kg_max": 600.0,
            "valid_as_of": date(2026, 9, 1)
        }
    },
    {
        "method": "fungi",
        "common_name": "Lion's Mane",
        "image_url": "https://images.unsplash.com/photo-1591857177580-dc82b9ac4e1e?auto=format&fit=crop&w=800&q=80",
        "scientific_name": "Hericium erinaceus",
        "description": "Distinctive icicle-like nootropic medicinal and culinary mushroom known for nerve growth factor (NGF) stimulation and gourmet seafood texture.",
        "typical_harvest_days_min": 30,
        "typical_harvest_days_max": 45,
        "yield_kg_per_sqm_cycle_min": 0.8,
        "yield_kg_per_sqm_cycle_max": 1.5,
        "environmental": {
            "temp_min_c": 15.0, "temp_max_c": 25.0, "temp_optimum_c": 20.0,
            "humidity_min_pct": 70.0, "humidity_max_pct": 95.0,
            "light_requirement": "low", "photoperiod_hours": 6.0,
            "co2_ppm_min": 500, "co2_ppm_max": 900, "ventilation_required": True,
            "notes": "High CO2 causes coral-like branching; high fresh air exchange produces dense spiny globes."
        },
        "water": {
            "water_litres_per_kg_min": 5.0, "water_litres_per_kg_max": 10.0,
            "ph_min": 5.5, "ph_max": 7.0, "ec_min_ms_cm": None, "ec_max_ms_cm": None,
            "water_recycling_potential": "low", "water_quality_notes": "Ultrasonic misting."
        },
        "nutrients": {
            "nitrogen_n": "Wheat/Oat bran supplement (15-20%)", "phosphorus_p": "Wood ash minerals",
            "potassium_k": "Hardwood mineral content", "calcium_ca": "Gypsum (1-2%)",
            "carbon_source": "Hardwood sawdust (Oak, Beech, Alder)",
            "notes": "Fast mycelial run (14-21 days) followed by rapid fruiting (10-14 days)."
        },
        "substrate": {
            "primary_substrate": "Supplemented Hardwood Sawdust (Master's Mix: 50% Hardwood + 50% Soybean hulls)",
            "alternative_substrates": "Hardwood sawdust + 20% wheat bran",
            "substrate_moisture_pct_min": 60.0, "substrate_moisture_pct_max": 65.0,
            "sterilization_required": True,
            "notes": "Autoclaved micro-filter spawn bags."
        },
        "infrastructure": {
            "tanks_required": False, "pumps_required": False, "racks_required": True,
            "lighting_required": True, "climate_control_required": True,
            "growing_media": "Autoclaved sawdust grow bags with top/side slit",
            "estimated_capex_inr_per_sqm_min": 900.0, "estimated_capex_inr_per_sqm_max": 1850.0,
            "infrastructure_details": ["Autoclave", "Inoculation flow bench", "High-humidity fruiting room with fresh air exchange (FAE) fan"]
        },
        "nutrition": {
            "calories_kcal": 35.0, "protein_g": 2.5, "carbohydrates_g": 7.6, "fat_g": 0.3, "fiber_g": 2.8,
            "vitamin_a_ug": 0.0, "vitamin_b12_ug": 0.0, "vitamin_c_mg": 0.0, "vitamin_d_ug": 0.6,
            "vitamin_e_mg": 0.0, "vitamin_k_ug": 0.0, "calcium_mg": 6.0, "iron_mg": 0.8,
            "magnesium_mg": 16.0, "potassium_mg": 380.0, "zinc_mg": 0.9, "serving_basis": "per 100g fresh weight"
        },
        "cost_assumptions": {
            "electricity_inr_per_kg": 20.0, "water_inr_per_kg": 2.0, "nutrients_inr_per_kg": 10.0,
            "seeds_spawn_inr_per_kg": 18.0, "substrate_inr_per_kg": 25.0, "labor_inr_per_kg": 28.0,
            "maintenance_inr_per_kg": 6.0, "packaging_inr_per_kg": 10.0, "transport_inr_per_kg": 8.0,
            "indicative_price_inr_per_kg_min": 450.0, "indicative_price_inr_per_kg_max": 850.0,
            "valid_as_of": date(2026, 9, 1)
        }
    }
]
