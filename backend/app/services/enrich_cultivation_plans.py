"""
AgriSmart AI — Enrich Cultivation Plans with Infrastructure & Logistics Data
"""

import os
import sys
import json

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app import create_app, db
from backend.app.models.cultivation import Product

# Infrastructure & Logistics profiles mapped by crop common name
SPECS_DATA = {
    "Lettuce": {
        "infrastructure": {
            "system_type": "Nutrient Film Technique (NFT) Channels / DWC Rafts",
            "growing_media": "Rockwool Plugs / Oasis Horticubes / Phenolic Foam",
            "tanks_and_pumps": "500L Food-Grade UV-Stabilized Reservoir, 1800 L/h Submersible Magnetic Drive Pump with bypass valve",
            "lighting_and_dli": "Full Spectrum LED Grow Lights (6500K + 660nm Deep Red), Target DLI: 14–17 mol/m²/day, PPFD: 200–250 µmol/m²/s",
            "climate_and_hvac": "Evaporative Cooling Pads + Exhaust Fans with Positive Pressure Air Filtration; Automated Ultrasonic Mist (RH 60–70%)",
            "monitoring_sensors": "Continuous Inline pH (5.6–6.0), Toroidal EC (1.4–1.8 mS/cm), Dissolved Oxygen (>7.0 mg/L), Ambient Temp/RH",
            "power_backup": "3.0 kVA Online UPS / Solar Hybrid Inverter with Auto-Phase Transfer (minimum 4h continuous run for aeration)",
            "capex_breakdown_sqm": "₹ 650 – ₹ 1,100 per m²"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C (Pre-cooled immediately within 60 mins of harvest)",
            "storage_humidity_pct": "95% – 98% RH to eliminate moisture transpiration loss",
            "cold_chain_required": "Mandatory Continuous Cold Chain (Reefer transport required)",
            "max_transit_time_hours": "12 – 24 Hours from farm gate to retail dark store / supermarket",
            "max_distribution_radius_km": "180 – 250 km (Ultra-fresh same-day/next-morning delivery)",
            "packaging_standard": "Breathable anti-fog micro-perforated PET clamshells (150g/200g) or living-lettuce root-wrap pouches with batch QR",
            "expected_spoilage_pct": "< 2.0% with cold chain (vs 22% in traditional uncooled transit)",
            "target_sales_channels": "Quick-Commerce (Blinkit, Zepto, Swiggy Instamart), Gourmet Supermarkets (Nature's Basket), Premium B2B HoReCa"
        }
    },
    "Spinach": {
        "infrastructure": {
            "system_type": "Deep Water Culture (DWC) Troughs / NFT Gullies",
            "growing_media": "Rockwool Cubes / Cocopeat Net Pots (50mm)",
            "tanks_and_pumps": "750L Insulated Cold-Water Sump, 2400 L/h High-Flow Water Chiller circulation pump, Heavy-duty air blower diffuser rings",
            "lighting_and_dli": "Cool White + Hyper Red Horticultural LEDs, Target DLI: 12–15 mol/m²/day, PPFD: 180–220 µmol/m²/s (14h photoperiod)",
            "climate_and_hvac": "Dedicated Water Chiller maintaining nutrient solution at 18–20°C to prevent Pythium root-rot; Dehumidifier unit",
            "monitoring_sensors": "Solution Temp Probe, Inline EC (1.4–1.8 mS/cm), Dual pH Sensors (5.8–6.2), DO Probe (> 7.5 mg/L)",
            "power_backup": "3.5 kVA Solar Inverter + Generator Backup for Chiller and Aeration systems",
            "capex_breakdown_sqm": "₹ 700 – ₹ 1,200 per m²"
        },
        "logistics": {
            "storage_temperature_c": "1°C – 3°C (Rapid forced-air pre-cooling or hydro-cooling)",
            "storage_humidity_pct": "95% – 98% RH",
            "cold_chain_required": "Mandatory Strict Cold Chain (High respiration rate leafy green)",
            "max_transit_time_hours": "12 – 18 Hours to preserve crispness and vitamin C density",
            "max_distribution_radius_km": "150 – 200 km local metro consumption cluster",
            "packaging_standard": "Sealed modified-atmosphere packaging (MAP) pillow bags (250g) with nitrogen flush, anti-crush crate inserts",
            "expected_spoilage_pct": "< 3.0% under cold chain (vs 28% open ambient)",
            "target_sales_channels": "D2C Fresh Subscription Boxes, Premium Salad Bars, Modern Grocery Retail Chains, Institutional Cloud Kitchens"
        }
    },
    "Kale": {
        "infrastructure": {
            "system_type": "Vertical A-Frame NFT Channels / Dutch Bucket Towers",
            "growing_media": "Expanded Clay Aggregate (Hydroton) / Rockwool Plugs",
            "tanks_and_pumps": "600L Nutrient Sump Tank, High-Head Submersible Pump 2800 L/h, Multi-tier manifold distribution",
            "lighting_and_dli": "High-Efficiency LED Bars, Target DLI: 16–20 mol/m²/day, PPFD: 250–300 µmol/m²/s",
            "climate_and_hvac": "Evaporative Cooling System + High-Volume Low-Speed (HVLS) circulation fans, Night-time temperature suppression (15–18°C)",
            "monitoring_sensors": "Continuous pH (5.8–6.4), High-EC Sensor (1.8–2.4 mS/cm), Quantum PAR Sensor",
            "power_backup": "2.5 kVA Backup System",
            "capex_breakdown_sqm": "₹ 750 – ₹ 1,250 per m²"
        },
        "logistics": {
            "storage_temperature_c": "1°C – 4°C",
            "storage_humidity_pct": "90% – 95% RH",
            "cold_chain_required": "Recommended Refrigerated Cold Chain",
            "max_transit_time_hours": "24 – 36 Hours (High post-harvest durability)",
            "max_distribution_radius_km": "300 – 450 km regional supply radius",
            "packaging_standard": "Perforated kraft paper wraps / recyclable PLA breathable pouches (200g/500g) packed in sturdy plastic returnable crates",
            "expected_spoilage_pct": "< 2.0% under cold-chain",
            "target_sales_channels": "Organic Superfood Retail, Health Food Brands, Smoothie & Cold-Pressed Juice Outlets, B2B Fine Dining"
        }
    },
    "Basil": {
        "infrastructure": {
            "system_type": "Nutrient Film Technique (NFT) Gully Channels / Vertical Towers",
            "growing_media": "Rockwool Cubes / Phenolic Foam / Coco Discs",
            "tanks_and_pumps": "450L Polyethylene Tank, 1500 L/h Pump with aeration venturi nozzle",
            "lighting_and_dli": "High-Intensity LED (Rich Blue Spectrum 450nm for essential oil synthesis), DLI: 16–22 mol/m²/day, PPFD: 250–350 µmol/m²/s",
            "climate_and_hvac": "Warm CEA Climate Control (22–27°C Day, 18–20°C Night, RH 55–65%); Active dehumidification to prevent Botrytis fungal blight",
            "monitoring_sensors": "EC Sensor (1.0–1.6 mS/cm), pH Sensor (5.5–6.2), Ambient PAR & Leaf Temperature IR sensor",
            "power_backup": "2.0 kVA Inverter system",
            "capex_breakdown_sqm": "₹ 600 – ₹ 1,000 per m²"
        },
        "logistics": {
            "storage_temperature_c": "10°C – 12°C (CRITICAL: DO NOT cool below 10°C to avoid irreversible chilling injury / leaf blackening)",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Temperature-Controlled Ambient/Chilled (10–12°C dedicated zone)",
            "max_transit_time_hours": "12 – 24 Hours to maintain volatile aroma and essential oil integrity",
            "max_distribution_radius_km": "200 km local metropolitan radius",
            "packaging_standard": "Upright vented standing pouches / living basil pots with sealed root reservoir, breathable film",
            "expected_spoilage_pct": "< 3.5% with proper 11°C transit",
            "target_sales_channels": "Italian Pizzerias, Pesto Manufacturers, Fine Dining Continental Restaurants, Luxury Hotel Kitchens"
        }
    },
    "Mint": {
        "infrastructure": {
            "system_type": "NFT Gullies / DWC Rafts / Horizontal Troughs",
            "growing_media": "Rockwool Plugs / Coarse Perlite & Cocopeat 50:50",
            "tanks_and_pumps": "500L Reservoir, 1800 L/h pump, automated sub-surface drip irrigation",
            "lighting_and_dli": "Full Spectrum LEDs, DLI: 14–18 mol/m²/day, PPFD: 200–260 µmol/m²/s",
            "climate_and_hvac": "Evaporative Cooling pad-fan system (20–25°C, RH 60–70%), continuous exhaust air circulation",
            "monitoring_sensors": "Inline pH (5.5–6.5), EC (1.4–2.0 mS/cm), Sump Level ultrasonic sensor",
            "power_backup": "2.0 kVA Inverter",
            "capex_breakdown_sqm": "₹ 550 – ₹ 950 per m²"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C",
            "storage_humidity_pct": "95% RH",
            "cold_chain_required": "Mandatory Cold Chain",
            "max_transit_time_hours": "24 Hours",
            "max_distribution_radius_km": "200 km",
            "packaging_standard": "Perforated LDPE polybags / 100g plastic punnets with moisture absorption pads",
            "expected_spoilage_pct": "< 2.5%",
            "target_sales_channels": "Commercial Beverage Bars, Cocktail Lounges, Herbal Tea Processors, Central Institutional Kitchens"
        }
    },
    "Coriander": {
        "infrastructure": {
            "system_type": "Dense-Seeded NFT Gully Channels / Ebb & Flow Tables",
            "growing_media": "Sterile Cocopeat Mesh Beds / Rockwool Mats",
            "tanks_and_pumps": "400L Tank, 1600 L/h Magnetic Submersible Pump",
            "lighting_and_dli": "LED Grow Bars (6500K), DLI: 12–16 mol/m²/day, PPFD: 180–220 µmol/m²/s",
            "climate_and_hvac": "Cool CEA Microclimate (17–22°C; strict temperature limit < 25°C to avoid premature bolting and flowering)",
            "monitoring_sensors": "pH Sensor (5.8–6.5), EC Sensor (1.2–1.6 mS/cm), Sump Temp Probe",
            "power_backup": "2.0 kVA Inverter",
            "capex_breakdown_sqm": "₹ 500 – ₹ 900 per m²"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C",
            "storage_humidity_pct": "95% RH",
            "cold_chain_required": "Mandatory Cold Chain",
            "max_transit_time_hours": "12 – 18 Hours",
            "max_distribution_radius_km": "150 km",
            "packaging_standard": "Root-intact banded bunches in ventilated food-grade plastic sleeves (100g/250g)",
            "expected_spoilage_pct": "< 3.0%",
            "target_sales_channels": "Daily Essential Grocery Retailers, Online Grocery Delivery Platforms, Commercial Catering"
        }
    },
    "Tomato": {
        "infrastructure": {
            "system_type": "Bato Buckets (Dutch Buckets) / Coir Slab Drip Irrigation",
            "growing_media": "100% Buffered Cocopeat / Perlite Grow Bags (1m slabs)",
            "tanks_and_pumps": "1000L Triple-tank A/B/Acid fertigation injection skid, Pressure-compensating drippers (2 L/h per plant)",
            "lighting_and_dli": "Top High-Bay LED / Supplemental Interlighting, DLI: 22–30 mol/m²/day, PPFD: 400–600 µmol/m²/s",
            "climate_and_hvac": "Automated Greenhouse Venting + Shading Screen + Evaporative Cooling; CO2 enrichment injection (800–1000 ppm)",
            "monitoring_sensors": "Multi-point PAR, Rootzone Moisture TDR probe, EC/pH inline Dosatron, Thermal Imaging Canopy sensors",
            "power_backup": "5.0 kVA Generator + Solar Hybrid System",
            "capex_breakdown_sqm": "₹ 900 – ₹ 1,600 per m²"
        },
        "logistics": {
            "storage_temperature_c": "12°C – 14°C for breaker/turning stage; 10°C – 12°C for ripe tomatoes (Never refrigerate < 10°C to protect flavor esters)",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Temperature-Controlled Transit (12–14°C)",
            "max_transit_time_hours": "48 – 72 Hours",
            "max_distribution_radius_km": "500 – 800 km interstate distribution radius",
            "packaging_standard": "Corrugated export-grade vented cartons with molded cardboard cell trays (5kg/10kg bulk) or retail punnets (500g)",
            "expected_spoilage_pct": "< 2.0%",
            "target_sales_channels": "Modern Supermarket Retailers, Gourmet Salad Chains, Interstate Produce Aggregators, Export Markets"
        }
    },
    "Cucumber": {
        "infrastructure": {
            "system_type": "Dutch Bucket High-Wire Trellising / Coco Slab Hydroponics",
            "growing_media": "Cocopeat Slabs / Perlite Gro-bags",
            "tanks_and_pumps": "800L Fertigation Sump, Automated Drip Emitter Manifold (2.5 L/h per vine)",
            "lighting_and_dli": "Supplemental LED Overhead Arrays, DLI: 20–25 mol/m²/day, PPFD: 350–500 µmol/m²/s",
            "climate_and_hvac": "Climate Computer controlling side-curtain vents, roof foggers (22–26°C Day, 18–20°C Night, RH 70–80%)",
            "monitoring_sensors": "Inline EC (1.8–2.2 mS/cm), pH (5.5–6.0), Substrate Runoff EC/Volume logging sensor",
            "power_backup": "3.5 kVA Solar Inverter",
            "capex_breakdown_sqm": "₹ 800 – ₹ 1,400 per m²"
        },
        "logistics": {
            "storage_temperature_c": "10°C – 12°C",
            "storage_humidity_pct": "90% – 95% RH",
            "cold_chain_required": "Temperature-Controlled Transit (10–12°C)",
            "max_transit_time_hours": "36 – 48 Hours",
            "max_distribution_radius_km": "400 km",
            "packaging_standard": "Individual heat-shrink film wrap (protects against moisture loss) packed in 5kg telescopic cartons",
            "expected_spoilage_pct": "< 1.5%",
            "target_sales_channels": "Gourmet Salads & Sandwich Chains, Quick-Commerce Platforms, Hotel Buffet Suppliers"
        }
    },
    "Bell Pepper": {
        "infrastructure": {
            "system_type": "Dutch Buckets / Slab Drip Fertigation with 2-Leader Trellising",
            "growing_media": "70:30 Cocopeat / Perlite Mix in UV-treated Grow Bags",
            "tanks_and_pumps": "800L Dual-Tank Fertigation System with automated acid dosing pump",
            "lighting_and_dli": "High-DLI LED Bars, Target DLI: 20–26 mol/m²/day, PPFD: 350–500 µmol/m²/s",
            "climate_and_hvac": "Greenhouse Climate Automation (21–25°C Day, 17–19°C Night, RH 60–70%); Shading curtains for solar radiation control",
            "monitoring_sensors": "Drainage volume flowmeter, EC (2.0–2.6 mS/cm), pH (5.8–6.3), Solar Pyranometer",
            "power_backup": "3.5 kVA Hybrid System",
            "capex_breakdown_sqm": "₹ 850 – ₹ 1,500 per m²"
        },
        "logistics": {
            "storage_temperature_c": "8°C – 10°C",
            "storage_humidity_pct": "90% – 95% RH",
            "cold_chain_required": "Refrigerated Transport (8–10°C)",
            "max_transit_time_hours": "48 – 72 Hours",
            "max_distribution_radius_km": "600 km",
            "packaging_standard": "Multi-colored tri-pack punnets (Red/Yellow/Green) in vented cardboard display outers",
            "expected_spoilage_pct": "< 2.0%",
            "target_sales_channels": "Premium Supermarkets, Modern Trade, Continental Restaurant Chains, Export Wholesalers"
        }
    },
    "Strawberry": {
        "infrastructure": {
            "system_type": "Elevated Table-Top Gutter Hydroponics / Vertical Aeroponic Columns",
            "growing_media": "Cocopeat + Perlite 60:40 with Slow-Release Base",
            "tanks_and_pumps": "600L Chilled Nutrient Reservoir, Multi-zone Micro-Drip Emitters with anti-drain valves",
            "lighting_and_dli": "Far-Red + Deep-Red Floral Induction LEDs, DLI: 16–22 mol/m²/day, PPFD: 250–350 µmol/m²/s",
            "climate_and_hvac": "Dedicated Precision HVAC (18–22°C Day, 10–14°C Night to induce anthocyanin sweetness, RH 60–70%)",
            "monitoring_sensors": "Rootzone Chiller Temp Probe (16–18°C), Inline EC (1.0–1.4 mS/cm), pH (5.5–6.0), Brix refractometer",
            "power_backup": "5.0 kVA Generator + UPS (Crucial for root cooling and ventilation)",
            "capex_breakdown_sqm": "₹ 1,100 – ₹ 1,800 per m²"
        },
        "logistics": {
            "storage_temperature_c": "0°C – 2°C (Forced-air rapid cooling within 45 minutes of delicate hand-picking)",
            "storage_humidity_pct": "90% – 95% RH",
            "cold_chain_required": "Mandatory High-Precision Cold Chain (0–2°C strict)",
            "max_transit_time_hours": "12 – 24 Hours",
            "max_distribution_radius_km": "250 km (Ultra-perishable premium commodity)",
            "packaging_standard": "Shock-absorbing clear PET hinged punnets (200g) with bubble-cushion bottom pads, tamper-evident security seal",
            "expected_spoilage_pct": "< 3.0% with uninterrupted 1°C cold-chain",
            "target_sales_channels": "Luxury Dessert & Bakery Chains, Gourmet Retail, Direct-to-Consumer Fresh Fruit Subscriptions"
        }
    },
    "Microgreens": {
        "infrastructure": {
            "system_type": "Vertical Multi-Tier Automated Racks (4–6 Tiers) with Ebb & Flow Trays",
            "growing_media": "Hemp / Jute Fiber Grow Mats / Food-Grade Sterile Cellulose Pads",
            "tanks_and_pumps": "300L Central Tank with Automated Recirculating Flood-and-Drain Valve System",
            "lighting_and_dli": "High-Efficiency 4000K Full Spectrum LED Strips (1 per shelf tier), PPFD: 120–160 µmol/m²/s, DLI: 8–10 mol/m²/day",
            "climate_and_hvac": "Indoor Clean-Room Environmental Chamber (20–22°C, RH 50–60%), Continuous Micro-Air Flow Fans over each shelf",
            "monitoring_sensors": "Ambient Temp/Humidity Data Logger, Automated Flood Cycle Digital Timers, pH Sensor (5.8–6.5)",
            "power_backup": "2.0 kVA Inverter system",
            "capex_breakdown_sqm": "₹ 1,200 – ₹ 2,200 per m² (High vertical density)"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Mandatory Continuous Cold Chain",
            "max_transit_time_hours": "12 – 24 Hours (Fresh cut) or 5–7 Days (Live root trays)",
            "max_distribution_radius_km": "100 – 150 km local urban perimeter",
            "packaging_standard": "Crystal clear recycled PET clamshells (50g/100g) or Live-Harvest biodegradable seedling trays",
            "expected_spoilage_pct": "< 2.0%",
            "target_sales_channels": "High-End Gastronomy, Michelin & 5-Star Hotel Chefs, Wellness Juice Bars, Specialty Foodservice"
        }
    },
    "Spirulina": {
        "infrastructure": {
            "system_type": "HDPE-Lined Open Raceway Ponds (0.3m depth) / Closed Tubular Photobioreactors (PBR)",
            "growing_media": "Zarrouk Alkaline Mineral Medium (pH 9.2–10.5, Sodium Bicarbonate buffer)",
            "tanks_and_pumps": "8-Blade PVC Paddlewheel (Continuous culture velocity 20–30 cm/s), Slurry Harvest Diaphragm Pump",
            "lighting_and_dli": "Natural Solar Sunlight in Polyhouse / Supplemental High-Lux PAR Lighting (30,000–45,000 Lux)",
            "climate_and_hvac": "Solar Polyhouse Tunnel with Automated Foggers (Culture Temp: 30–35°C optimum, ambient < 38°C)",
            "monitoring_sensors": "Optical Density Spectrophotometer (OD 560nm), Continuous High-Range pH Probe, DO Sensor, Microscope for purity checks",
            "power_backup": "3.5 kVA Solar Hybrid Inverter (Continuous paddlewheel agitation prevents culture settling and anoxia)",
            "capex_breakdown_sqm": "₹ 450 – ₹ 950 per m²"
        },
        "logistics": {
            "storage_temperature_c": "Ambient (Dry powder / flakes in dark sealed container) OR -18°C Frozen (Live fresh biomass paste)",
            "storage_humidity_pct": "< 50% RH for dry powder; 0% for vacuum pouches",
            "cold_chain_required": "Not required for dry powder (24M shelf-life); Mandatory -18°C for fresh living paste",
            "max_transit_time_hours": "30 Days (Dry powder worldwide shipping) / 24 Hours (Fresh frozen paste in dry-ice containers)",
            "max_distribution_radius_km": "Global / Nationwide export for dried nutraceutical grade biomass",
            "packaging_standard": "Multi-layer vacuum-sealed aluminum barrier pouches (100g/250g/1kg) with oxygen scavenger sachets, Nitrogen flushed",
            "expected_spoilage_pct": "< 0.5%",
            "target_sales_channels": "Nutraceutical Companies, Protein Supplement Brands, Food Fortification Manufacturers, Direct Export"
        }
    },
    "Chlorella": {
        "infrastructure": {
            "system_type": "Closed Borosilicate Glass Photobioreactors (PBR) / Circular Agitated Ponds",
            "growing_media": "BG-11 / Modified Bold's Basal Nutrient Medium",
            "tanks_and_pumps": "Centrifugal Disc-Stack Harvesting Centrifuge, High-Pressure Cell Wall Disrupter homogenizer",
            "lighting_and_dli": "Narrow-Band Red/Blue LED Illuminators + Natural Solar Concentration",
            "climate_and_hvac": "Enclosed Sterile Clean-Room Facility, Automated CO2 Gas Injection Sparging System (pH maintained 6.8–7.5)",
            "monitoring_sensors": "Inline Optical Density Turbidity Probe, Dissolved CO2/O2 analyzer, Flow Cytometer for microbial count",
            "power_backup": "6.0 kVA Industrial UPS",
            "capex_breakdown_sqm": "₹ 1,500 – ₹ 3,000 per m²"
        },
        "logistics": {
            "storage_temperature_c": "15°C – 25°C (Hermetically sealed dry powder)",
            "storage_humidity_pct": "< 45% RH",
            "cold_chain_required": "Standard Ambient Dry Logistics",
            "max_transit_time_hours": "Nationwide / Export Cargo (60 Days+)",
            "max_distribution_radius_km": "Global Distribution",
            "packaging_standard": "UV-blocking nitrogen-flushed metallic barrier pouches / Food-grade HDPE drums with desiccant seals",
            "expected_spoilage_pct": "< 0.2%",
            "target_sales_channels": "Dietary Supplement Brands, Cosmetic & Skin-Care Formulation Labs, Functional Beverage Manufacturers"
        }
    },
    "Oyster Mushroom": {
        "infrastructure": {
            "system_type": "Vertical Hanging Poly-Bag Racks / Wire-Mesh Growing Shelves",
            "growing_media": "Pasteurized Paddy Straw / Wheat Straw / Sawdust (65% moisture)",
            "tanks_and_pumps": "Substrate Pasteurization Boiler / Steam Vat, Ultrasonic Humidifier with 4-way misting nozzles",
            "lighting_and_dli": "Indirect Diffuse Cool White LED (500–1000 Lux for fruiting pinhead induction, 0h light during spawn run)",
            "climate_and_hvac": "Insulated Fruiting Chamber (22–26°C, RH 85–92%), Negative-pressure exhaust blower (CO2 < 900 ppm)",
            "monitoring_sensors": "NDIR CO2 Sensor (0–5000 ppm), Dual Dry/Wet Bulb RH sensor, Substrate Internal Core Temperature probe",
            "power_backup": "2.5 kVA Backup System",
            "capex_breakdown_sqm": "₹ 400 – ₹ 750 per m²"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C (Immediate pre-cooling upon harvest)",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Mandatory Refrigerated Cold Chain",
            "max_transit_time_hours": "18 – 24 Hours",
            "max_distribution_radius_km": "200 km",
            "packaging_standard": "Breathable micro-perforated polypropylene punnets (200g) with absorbent cellulose bottom pad",
            "expected_spoilage_pct": "< 2.5%",
            "target_sales_channels": "Gourmet Dining Restaurants, Fresh Produce Supermarkets, Vegan/Plant-Based Food Outlets, Local Farmers Markets"
        }
    },
    "Shiitake": {
        "infrastructure": {
            "system_type": "Vertical Growing Racks for Synthetic Sawdust Fruiting Blocks / Hardwood Logs",
            "growing_media": "Oak/Hardwood Sawdust supplemented with 20% Wheat Bran & 1% Gypsum (Autoclaved at 121°C)",
            "tanks_and_pumps": "High-Pressure Steam Autoclave, Cold Shock Immersion Water Tank (10–12°C for pinning trigger)",
            "lighting_and_dli": "Indirect Cool White LED (800–1200 Lux, 8–12h daily during fruiting)",
            "climate_and_hvac": "Precision Climate Room (Incubation 22–25°C in dark; Fruiting 16–20°C, RH 80–85%), Air filtration (HEPA H14)",
            "monitoring_sensors": "Continuous CO2 Sensor (< 1000 ppm), High-Precision Temp/RH Datalogger, Substrate Hydration Sensor",
            "power_backup": "3.5 kVA Inverter",
            "capex_breakdown_sqm": "₹ 700 – ₹ 1,300 per m²"
        },
        "logistics": {
            "storage_temperature_c": "1°C – 3°C (Rapid forced-air chilled storage)",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Mandatory Strict Cold Chain",
            "max_transit_time_hours": "36 – 48 Hours for fresh / 12 Months for sun-dried Shiitake",
            "max_distribution_radius_km": "350 km for fresh / Global for dried mushroom products",
            "packaging_standard": "Rigid thermoformed plastic punnets (150g/200g) with micro-vented lidding film or vacuum packs for dried",
            "expected_spoilage_pct": "< 2.0%",
            "target_sales_channels": "Japanese/Pan-Asian Specialty Restaurants, Premium Supermarkets, Medicinal Mushroom Extractors, Gourmet B2B"
        }
    },
    "Button Mushroom": {
        "infrastructure": {
            "system_type": "Multi-Tier Dutch Aluminum Shelving (6 Tiers) with Automated Casing Layer Application",
            "growing_media": "Composted Wheat Straw + Poultry Manure + Gypsum with Peat Moss / Spent Compost Casing Layer",
            "tanks_and_pumps": "Phase II/III Compost Bulk Pasteurization Tunnel with aerated floor, High-Volume AHU with steam injection",
            "lighting_and_dli": "Complete Darkness during vegetative run and cropping (Minimal service lighting)",
            "climate_and_hvac": "Industrial Air Handling Units (AHU) with chilled water coils (Spawn run 24°C, Pinning cool-down to 16–18°C, RH 85–90%)",
            "monitoring_sensors": "Multi-tier Compost Core Temp Probes (PT100), Room CO2 Controller (Flushing down to 800 ppm for pinning)",
            "power_backup": "7.5 kVA Commercial Diesel Generator + UPS (Essential for continuous AHU ventilation and cooling)",
            "capex_breakdown_sqm": "₹ 1,200 – ₹ 2,200 per m²"
        },
        "logistics": {
            "storage_temperature_c": "1°C – 3°C (Vacuum cooling within 2 hours of picking prevents cap opening/browning)",
            "storage_humidity_pct": "90% – 95% RH",
            "cold_chain_required": "Mandatory Refrigerated Cold Chain",
            "max_transit_time_hours": "24 – 36 Hours",
            "max_distribution_radius_km": "350 km regional consumption cluster",
            "packaging_standard": "Vented cardboard cartons / 200g blue punnets with breathable stretch wrap",
            "expected_spoilage_pct": "< 3.0%",
            "target_sales_channels": "Large-Scale Supermarket Chains, Pizza Chains, Wholesale Mandis, Food Canning & Processing Units"
        }
    },
    "Lion's Mane": {
        "infrastructure": {
            "system_type": "Vertical Heavy-Duty Stainless Steel Rack Shelving in Sealed Grow Chambers",
            "growing_media": "Enriched Hardwood Sawdust + Soy Hulls (50:50 Master's Mix) in Filter-Patch Mycology Grow Bags",
            "tanks_and_pumps": "Commercial Autoclave Sterilizer (15 PSI, 121°C for 2.5 hrs), High-Output Ultrasonic Piezo Fogger System",
            "lighting_and_dli": "Diffuse Indirect 6000K LED (500–800 Lux, 12h photoperiod for spine elongation)",
            "climate_and_hvac": "Dedicated Clean Grow Chamber (18–22°C, RH 88–95% ultra-high humidity, Continuous fresh air CO2 < 800 ppm)",
            "monitoring_sensors": "Dual Industrial Capacitive RH Sensor, NDIR CO2 PPM Sensor, Substrate Moisture Scale",
            "power_backup": "3.0 kVA Online UPS",
            "capex_breakdown_sqm": "₹ 800 – ₹ 1,450 per m²"
        },
        "logistics": {
            "storage_temperature_c": "2°C – 4°C",
            "storage_humidity_pct": "85% – 90% RH",
            "cold_chain_required": "Mandatory Cold Chain (Delicate icicle-like spines prone to bruising)",
            "max_transit_time_hours": "18 – 24 Hours for fresh / 24 Months for freeze-dried nootropic powder",
            "max_distribution_radius_km": "200 km for fresh produce / Global for functional nootropic extracts",
            "packaging_standard": "Padded protective clamshells (150g) with individual cell dividers to prevent physical spine impact",
            "expected_spoilage_pct": "< 2.0%",
            "target_sales_channels": "Nootropic Supplement Formulators, Boutique Fine-Dining Chefs, Functional Mushroom D2C Brands, Wellness Clinics"
        }
    },
    "Milky Mushroom": {
        "infrastructure": {
            "system_type": "Vertical Hanging Wire Racks / Layered Slotted Angle Shelving",
            "growing_media": "Boiled / Steam-Pasteurized Chopped Paddy Straw + Soil/Sand Casing Layer (pH 7.8–8.2)",
            "tanks_and_pumps": "Substrate Soaking & Pasteurization Tank with immersion heaters, Fine atomizing misting nozzles",
            "lighting_and_dli": "Diffuse Ambient Natural Light / Low-Wattage LED (400–600 Lux during cropping)",
            "climate_and_hvac": "Tropical Warm CEA Chamber (Spawn Run: 28–32°C; Cropping: 30–35°C, RH 80–85% — ideal for tropical summer climates)",
            "monitoring_sensors": "Digital Thermohygrometer, Casing Layer Moisture Probe, CO2 Exhaust Controller (< 1200 ppm)",
            "power_backup": "2.0 kVA Inverter system",
            "capex_breakdown_sqm": "₹ 350 – ₹ 650 per m² (Lowest capex fungal crop)"
        },
        "logistics": {
            "storage_temperature_c": "4°C – 8°C (Longest natural shelf-life among all fresh edible mushrooms)",
            "storage_humidity_pct": "80% – 85% RH",
            "cold_chain_required": "Chilled / Air-Conditioned Transit",
            "max_transit_time_hours": "48 – 72 Hours (Robust non-browning firm white stipe)",
            "max_distribution_radius_km": "450 km interstate distribution",
            "packaging_standard": "Perforated polyethylene pouches (200g/500g) packed in sturdy plastic field crates",
            "expected_spoilage_pct": "< 1.5%",
            "target_sales_channels": "Tropical Regional Supermarkets, Indian Curry & Biryani Restaurants, Fresh Vegetable Mandis, Canning Units"
        }
    }
}

from sqlalchemy.orm.attributes import flag_modified

def enrich_and_seed():
    app = create_app('development')
    with app.app_context():
        updated_count = 0
        products = Product.query.all()
        for p in products:
            plan = dict(p.cultivation_plan or {})
            
            # 1. Match infrastructure & logistics specs
            matched_spec = None
            for key, spec in SPECS_DATA.items():
                if key.lower() in p.common_name.lower() or p.common_name.lower() in key.lower():
                    matched_spec = spec
                    break

            if matched_spec:
                infra = dict(matched_spec["infrastructure"])
                log = dict(matched_spec["logistics"])
                
                # Normalize aliases for logistics
                if "max_transit_time_hours" in log and "max_transit_time_hrs" not in log:
                    log["max_transit_time_hrs"] = log["max_transit_time_hours"]
                if "target_sales_channels" in log and "distribution_channels" not in log:
                    log["distribution_channels"] = log["target_sales_channels"]
                if "expected_spoilage_pct" in log and "spoilage_risk_profile" not in log:
                    log["spoilage_risk_profile"] = f"Expected Spoilage Rate: {log['expected_spoilage_pct']}"
                if "storage_temperature_c" in log and "shelf_life_days" not in log:
                    log["shelf_life_days"] = "7 – 14 Days (in recommended cold storage)"

                plan["infrastructure_specs"] = infra
                plan["logistics_specs"] = log

            # 2. Normalize and enrich stages
            raw_stages = plan.get("stages", [])
            normalized_stages = []
            for idx, stg in enumerate(raw_stages):
                s_num = stg.get("stage_number") or stg.get("stage") or (idx + 1)
                s_name = stg.get("stage_name") or stg.get("name") or f"Stage {s_num}"
                phase_name = stg.get("phase_name") or f"Stage {s_num}"
                timeline = stg.get("timeline") or stg.get("days") or f"Stage {s_num}"
                objective = stg.get("objective") or stg.get("protocol") or "Optimal growth and environmental control"
                protocol = stg.get("protocol") or objective
                
                tasks = stg.get("tasks") or []
                if not tasks and protocol:
                    tasks = [t.strip() + "." for t in protocol.replace("..", ".").split(". ") if t.strip()]
                    if not tasks:
                        tasks = [protocol]

                params = dict(stg.get("target_parameters") or stg.get("target_params") or {})
                risks = stg.get("risks_and_mitigation") or "Maintain sterile environment, prevent root pathogens, and monitor climate deviations."
                transition = stg.get("transition_criteria") or "Proceed to next phase when root system, biomass and leaf node count meet target benchmarks."

                norm_stage = {
                    "stage": s_num,
                    "stage_number": s_num,
                    "phase_name": phase_name,
                    "stage_name": s_name,
                    "name": s_name,
                    "days": timeline,
                    "timeline": timeline,
                    "objective": objective,
                    "protocol": protocol,
                    "tasks": tasks,
                    "target_parameters": params,
                    "target_params": params,
                    "risks_and_mitigation": risks,
                    "transition_criteria": transition
                }
                normalized_stages.append(norm_stage)

            plan["stages"] = normalized_stages
            if "total_duration_days" not in plan and "total_days" in plan:
                plan["total_duration_days"] = plan["total_days"]
            elif "total_duration_days" not in plan:
                plan["total_duration_days"] = f"{p.typical_harvest_days_min} – {p.typical_harvest_days_max} Days"

            p.cultivation_plan = plan
            flag_modified(p, "cultivation_plan")
            updated_count += 1
            print(f"Enriched and normalized [{p.common_name}] with {len(normalized_stages)} stages.")

        db.session.commit()
        print(f"Successfully committed {updated_count} products.")

if __name__ == '__main__':
    enrich_and_seed()
