"""
AgriSmart AI — Comprehensive Cultivation Lifecycle Plans (Day 1 to Selling)
===========================================================================
Populates full stage-by-stage agronomic cultivation protocols for all 18 crops.
"""

CULTIVATION_PLANS = {
    "Lettuce": {
        "total_days": "30–45 Days",
        "system_type": "Nutrient Film Technique (NFT) / Deep Water Culture (DWC)",
        "summary": "Rapid-turnaround leafy green with steady year-round commercial demand in urban food service.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Nursery Seeding & Germination",
                "timeline": "Day 1 – Day 4",
                "target_params": {"temperature": "20–22°C", "humidity": "85–90% RH", "light": "Darkness for 48h, then 100 µmol/m²/s", "ec_ph": "Pure RO water, pH 5.8"},
                "protocol": "Sow 1–2 coated seeds per rockwool / OASIS plug. Keep moist with fine mist. Move to nursery light rack upon radical emergence on Day 3."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Seedling Vegetative Stage",
                "timeline": "Day 5 – Day 14",
                "target_params": {"temperature": "19–23°C", "humidity": "65–70% RH", "light": "16h photoperiod (PPFD 180 µmol/m²/s)", "ec_ph": "EC 0.8–1.0 mS/cm, pH 5.8"},
                "protocol": "Introduce half-strength balanced nutrient solution. Develop 3–4 true leaves and vigorous white root filaments extending 3–5 cm below plug."
            },
            {
                "stage_number": 3,
                "stage_name": "Main NFT Channel Transplant & Canopy Expansion",
                "timeline": "Day 15 – Day 28",
                "target_params": {"temperature": "18–22°C Day / 16–18°C Night", "humidity": "60–65% RH", "light": "16h photoperiod (PPFD 250 µmol/m²/s)", "ec_ph": "EC 1.4–1.8 mS/cm, pH 5.6–6.0"},
                "protocol": "Transplant plugs into main NFT channels at 20cm spacing. Maintain water flow 1.5–2.0 L/min per gully. Keep dissolved oxygen (DO) > 7.0 mg/L. Air movement prevents inner tipburn."
            },
            {
                "stage_number": 4,
                "stage_name": "Pre-Harvest Head Densification & Nutrient Tuning",
                "timeline": "Day 29 – Day 35",
                "target_params": {"temperature": "17–20°C", "humidity": "55–60% RH", "light": "14h photoperiod", "ec_ph": "EC 1.2–1.4 mS/cm, pH 5.8"},
                "protocol": "Lower rootzone temperature to enhance crispness. Reduce nitrate levels slightly 48h before harvest to minimize tissue nitrates for premium organic certification."
            },
            {
                "stage_number": 5,
                "stage_name": "Harvesting & Laboratory Quality Ingestion",
                "timeline": "Day 35 – Day 38",
                "target_params": {"harvest_weight": "180–250g per head", "cleanliness": "Zero soil residue", "quality_tests": "E. coli (<10 CFU/g), Heavy Metals (<0.1 mg/kg)"},
                "protocol": "Harvest in early morning when turgor pressure is highest. Cut stem clean 5mm below basal leaves or pull with live root-cube for living-lettuce retail."
            },
            {
                "stage_number": 6,
                "stage_name": "Post-Harvest Hydro-cooling, Packaging & Market Handover",
                "timeline": "Day 38 – Day 40",
                "target_params": {"storage_temp": "2–4°C", "storage_rh": "95% RH", "packaging": "Vented PET clamshell / micro-perforated bag", "shelf_life": "14–18 Days"},
                "protocol": "Rapidly hydro-cool to 3°C within 60 minutes. Pack in sealed breathable clamshells with batch QR Quality Assurance Certificate. Ship via refrigerated cold-chain to HoReCa & premium retail at ₹140–200/kg."
            }
        ]
    },
    "Spinach": {
        "total_days": "28–42 Days",
        "system_type": "Deep Water Culture (DWC) / Nutrient Film Technique (NFT)",
        "summary": "Nutrient-dense iron and vitamin rich crop grown in cool water channels.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Cold Stratification & Germination",
                "timeline": "Day 1 – Day 5",
                "target_params": {"temperature": "16–18°C", "humidity": "90% RH", "light": "Darkness for 72h", "ec_ph": "RO water, pH 6.0"},
                "protocol": "Pre-chill seeds at 4°C for 24h to break dormancy. Sow in rockwool plugs. Keep substrate moist and cool."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Seedling Phase",
                "timeline": "Day 6 – Day 15",
                "target_params": {"temperature": "17–20°C", "humidity": "65% RH", "light": "14h photoperiod", "ec_ph": "EC 1.0–1.2 mS/cm, pH 6.0–6.5"},
                "protocol": "Supply mild nutrient formula. Maintain high airflow to prevent damping-off (Pythium)."
            },
            {
                "stage_number": 3,
                "stage_name": "DWC Raft Transplant & Deep Canopy Growth",
                "timeline": "Day 16 – Day 30",
                "target_params": {"temperature": "16–19°C (Water < 20°C)", "humidity": "60% RH", "light": "12–14h photoperiod", "ec_ph": "EC 1.6–2.0 mS/cm, pH 6.0–6.4"},
                "protocol": "Transplant into floating rafts at 15cm spacing. Ensure aggressive DO aeration (>8 mg/L). Iron chelate Fe-DTPA prevents leaf chlorosis."
            },
            {
                "stage_number": 4,
                "stage_name": "Baby Leaf vs Mature Bunch Harvest",
                "timeline": "Day 31 – Day 38",
                "target_params": {"harvest_stage": "Baby leaf (7–10cm) or Full rosette (15–20cm)", "temp": "15–18°C"},
                "protocol": "Selective outer leaf cut-and-come-again or single whole rosette root-shear harvest."
            },
            {
                "stage_number": 5,
                "stage_name": "Washing, MAP Packaging & Market Handover",
                "timeline": "Day 39 – Day 40",
                "target_params": {"cooling": "1–3°C blast chilling", "packaging": "Modified Atmosphere Packaging (MAP)", "shelf_life": "10–14 Days"},
                "protocol": "Sanitized ice-water dip, spin dry, pack in nitrogen-flushed MAP pillow pouches. Supply to salad processors and organic supermarkets at ₹100–160/kg."
            }
        ]
    },
    "Basil": {
        "total_days": "35–50 Days",
        "system_type": "Nutrient Film Technique (NFT) / Ebb & Flow",
        "summary": "High-margin culinary herb with intense aromatic essential oil production.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Warm Germination & Sprouting",
                "timeline": "Day 1 – Day 6",
                "target_params": {"temperature": "24–26°C", "humidity": "85% RH", "light": "16h photoperiod", "ec_ph": "EC 0.6 mS/cm, pH 5.8"},
                "protocol": "Sow 3–4 seeds per rockwool cube. Maintain warm bottom heat. Seedlings emerge in 4–5 days."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Vegetative & Apical Pinching",
                "timeline": "Day 7 – Day 18",
                "target_params": {"temperature": "22–25°C", "humidity": "65% RH", "light": "16h light (PPFD 220 µmol/m²/s)", "ec_ph": "EC 1.0–1.4 mS/cm, pH 5.8"},
                "protocol": "Pinch central apical shoot at 4th true leaf node to stimulate dense multi-stem lateral branching."
            },
            {
                "stage_number": 3,
                "stage_name": "Main NFT Channel Growth & Terpene Synthesis",
                "timeline": "Day 19 – Day 38",
                "target_params": {"temperature": "23–27°C", "humidity": "55–65% RH", "light": "18h light (PPFD 280 µmol/m²/s)", "ec_ph": "EC 1.8–2.2 mS/cm, pH 5.8–6.2"},
                "protocol": "High light and warm rootzone boost linalool and eugenol essential oils. Prune early flower buds immediately to prevent bitterness."
            },
            {
                "stage_number": 4,
                "stage_name": "Selective Shoot Harvesting & Grading",
                "timeline": "Day 39 – Day 45",
                "target_params": {"shoot_length": "12–15 cm", "defects": "Zero black spotting / tipburn"},
                "protocol": "Cut top 15cm stems above lower leaf nodes allowing continuous multi-cut regrowth every 12–14 days."
            },
            {
                "stage_number": 5,
                "stage_name": "Packaging (Non-Chilled) & Gourmet Delivery",
                "timeline": "Day 46 – Day 48",
                "target_params": {"storage_temp": "10–12°C (Do NOT store below 8°C)", "packaging": "Micro-perforated breathable herb sleeves", "shelf_life": "7–10 Days"},
                "protocol": "Pack in breathable transparent herb cones with stem bases moist. Deliver same-day to Italian restaurants, five-star hotels & pesto manufacturers at ₹180–300/kg."
            }
        ]
    },
    "Tomato": {
        "total_days": "75–100 Days",
        "system_type": "Dutch Bucket / Coco Coir Slab Drip Irrigation",
        "summary": "High-yield vine crop with continuous multi-month fruiting cycle.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Rockwool Seeding & Propagation",
                "timeline": "Day 1 – Day 8",
                "target_params": {"temperature": "24–26°C", "humidity": "80% RH", "light": "16h light upon emergence", "ec_ph": "EC 1.0 mS/cm, pH 5.8"},
                "protocol": "Sow in 25mm rockwool starter plugs. Keep warm with bottom heating."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Block Grafting & Root Development",
                "timeline": "Day 9 – Day 25",
                "target_params": {"temperature": "21–24°C", "humidity": "65% RH", "light": "PPFD 250 µmol/m²/s", "ec_ph": "EC 1.6–2.0 mS/cm, pH 5.8"},
                "protocol": "Transfer into 75mm rockwool cubes. Prune initial side shoots. Train strong single leader stem."
            },
            {
                "stage_number": 3,
                "stage_name": "Slab Transplant, High-Wire Trellising & Flowering",
                "timeline": "Day 26 – Day 55",
                "target_params": {"temperature": "22–26°C Day / 17–19°C Night", "humidity": "65–70% RH", "light": "High PPFD 400 µmol/m²/s", "ec_ph": "EC 2.2–2.8 mS/cm, pH 5.6–6.0"},
                "protocol": "Transplant onto coco coir grow slabs. Clip to overhead high-wire strings. Weekly de-suckering. Bumblebee pollination or mechanical truss vibration."
            },
            {
                "stage_number": 4,
                "stage_name": "Fruit Setting, Sugar Brix Enrichment & Ripening",
                "timeline": "Day 56 – Day 80",
                "target_params": {"temperature": "20–25°C", "humidity": "60% RH", "light": "High solar / LED", "ec_ph": "EC 2.8–3.5 mS/cm, pH 5.8"},
                "protocol": "Higher EC concentrates natural sugars (Brix > 7.5°). De-leaf lower canopy below ripening trusses for optimal air circulation."
            },
            {
                "stage_number": 5,
                "stage_name": "Truss Harvesting & Sugar Brix Verification",
                "timeline": "Day 81 – Day 90",
                "target_params": {"ripeness": "Stage 4–5 (Turning to Red-Ripe)", "calyx": "Intact green sepals"},
                "protocol": "Clip full trusses or individual fruit with calyx. Sort by size and color uniformity."
            },
            {
                "stage_number": 6,
                "stage_name": "Cushioned Carton Packaging & Retail Dispatch",
                "timeline": "Day 91 – Day 95",
                "target_params": {"storage_temp": "12–14°C", "packaging": "Molded pulp trays in ventilated cartons", "shelf_life": "14–21 Days"},
                "protocol": "Pack in layered cushioned boxes. Distribute to gourmet grocery chains & cloud kitchens at ₹60–140/kg."
            }
        ]
    },
    "Strawberry": {
        "total_days": "70–90 Days",
        "system_type": "Elevated Trough Substrate (Coco Coir + Perlite)",
        "summary": "Premium dessert fruit grown on waist-height ergonomic gutters.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Runner Plug Planting & Root Establishment",
                "timeline": "Day 1 – Day 10",
                "target_params": {"temperature": "18–22°C", "humidity": "80% RH", "light": "14h light", "ec_ph": "EC 0.8–1.0 mS/cm, pH 5.8–6.2"},
                "protocol": "Plant disease-free bare root / runner plugs in elevated coco-coir troughs. Keep crown level strictly at substrate surface."
            },
            {
                "stage_number": 2,
                "stage_name": "Vegetative Canopy & Crown Development",
                "timeline": "Day 11 – Day 30",
                "target_params": {"temperature": "18–21°C", "humidity": "65% RH", "light": "14h light", "ec_ph": "EC 1.2–1.4 mS/cm, pH 5.8"},
                "protocol": "Prune early runner shoots to force root and crown multiplication. Apply bio-fungicides to prevent crown rot."
            },
            {
                "stage_number": 3,
                "stage_name": "Truss Emergence, Flowering & Pollination",
                "timeline": "Day 31 – Day 55",
                "target_params": {"temperature": "18–20°C Day / 12–14°C Night", "humidity": "60–70% RH", "light": "PPFD 300 µmol/m²/s", "ec_ph": "EC 1.4–1.6 mS/cm, pH 5.8"},
                "protocol": "Deploy pollinator bees. Adjust potassium/calcium ratio. Place truss support tapes along trough edges to prevent stem kinking."
            },
            {
                "stage_number": 4,
                "stage_name": "Fruit Sizing & Anthocyanin Sugar Accumulation",
                "timeline": "Day 56 – Day 75",
                "target_params": {"temperature": "16–18°C Day / 10–12°C Night", "humidity": "55–60% RH", "light": "High light", "ec_ph": "EC 1.6–1.8 mS/cm, pH 5.8"},
                "protocol": "Cool night temperatures enhance brix sweetness and firm texture. Maintain strict calcium feeding to prevent tip-burn on calyx."
            },
            {
                "stage_number": 5,
                "stage_name": "Hand Picking at 90%+ Red Ripeness",
                "timeline": "Day 76 – Day 85",
                "target_params": {"harvest_time": "Early morning (< 15°C)", "handling": "Snap stem 1cm above berry without touching fruit surface"},
                "protocol": "Harvest directly into packaging punnets to eliminate secondary handling damage."
            },
            {
                "stage_number": 6,
                "stage_name": "Padded Punnets, Rapid Pre-Cooling & Luxury Sales",
                "timeline": "Day 86 – Day 88",
                "target_params": {"storage_temp": "1–2°C", "packaging": "250g clear PET punnet with bubble pad", "shelf_life": "7–10 Days"},
                "protocol": "Forced-air pre-cool to 2°C within 2 hours. Deliver to five-star pastry kitchens, luxury cafes & premium supermarkets at ₹350–650/kg."
            }
        ]
    },
    "Bell Pepper": {
        "total_days": "80–110 Days",
        "system_type": "Substrate Trough / Dutch Bucket Drip Irrigation",
        "summary": "High-value blocky sweet capsicum with thick walls and high shelf life.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Seed Germination & Propagation",
                "timeline": "Day 1 – Day 10",
                "target_params": {"temperature": "25–28°C", "humidity": "85% RH", "light": "Darkness for 5 days, then 16h light", "ec_ph": "EC 0.8 mS/cm, pH 5.8"},
                "protocol": "Sow in rockwool starter plugs with warm bottom heat."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Vegetative & Twin-Leader Training",
                "timeline": "Day 11 – Day 30",
                "target_params": {"temperature": "22–25°C", "humidity": "65% RH", "light": "16h light", "ec_ph": "EC 1.6–1.8 mS/cm, pH 5.8"},
                "protocol": "Prune seedling to two main 'V' leader branches. Transplant to slab."
            },
            {
                "stage_number": 3,
                "stage_name": "Canopy Trellising & Crown Flower Removal",
                "timeline": "Day 31 – Day 65",
                "target_params": {"temperature": "22–26°C Day / 18–20°C Night", "humidity": "65% RH", "light": "PPFD 350 µmol/m²/s", "ec_ph": "EC 2.2–2.6 mS/cm, pH 5.6–6.0"},
                "protocol": "Remove the first central crown flower to allow strong vegetative structure. Wind twin stems up vertical twine."
            },
            {
                "stage_number": 4,
                "stage_name": "Fruit Sizing & Color Turn Phase",
                "timeline": "Day 66 – Day 95",
                "target_params": {"temperature": "21–24°C", "humidity": "60% RH", "light": "High light", "ec_ph": "EC 2.4–2.8 mS/cm, pH 5.8"},
                "protocol": "Monitor color transition from green to vibrant Red/Yellow/Orange. Maintain high calcium and potassium to prevent blossom end rot."
            },
            {
                "stage_number": 5,
                "stage_name": "Harvesting & Export Quality Grading",
                "timeline": "Day 96 – Day 105",
                "target_params": {"color_uniformity": ">90% full color", "wall_thickness": ">6mm", "weight": "180–250g per fruit"},
                "protocol": "Clip stems cleanly 1cm above fruit shoulder. Grade for 4-lobed symmetry."
            },
            {
                "stage_number": 6,
                "stage_name": "Carton Packaging & Commercial Delivery",
                "timeline": "Day 106 – Day 110",
                "target_params": {"storage_temp": "8–10°C", "packaging": "5kg corrugated box with tissue liners", "shelf_life": "18–24 Days"},
                "protocol": "Store at 8–10°C (prevent chilling injury). Supply to hotel chains, QSRs & export markets at ₹80–180/kg."
            }
        ]
    },
    "Cucumber": {
        "total_days": "40–55 Days",
        "system_type": "High-Wire Drip Substrate System",
        "summary": "Fast-growing high-yield parthenocarpic cucumber with continuous daily flushes.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Rapid Seed Germination",
                "timeline": "Day 1 – Day 5",
                "target_params": {"temperature": "26–28°C", "humidity": "85% RH", "light": "18h light on Day 3", "ec_ph": "EC 1.0 mS/cm, pH 5.8"},
                "protocol": "Vigorous cotyledons emerge within 72 hours in rockwool cubes."
            },
            {
                "stage_number": 2,
                "stage_name": "Slab Transplant & Rapid Vertical Climbing",
                "timeline": "Day 6 – Day 18",
                "target_params": {"temperature": "23–26°C", "humidity": "75% RH", "light": "18h light", "ec_ph": "EC 1.6–1.8 mS/cm, pH 5.8"},
                "protocol": "Transplant to coco grow slabs. Plant climbs vertical twine at 10cm per day."
            },
            {
                "stage_number": 3,
                "stage_name": "Lateral Shoot Pruning & Fruit Induction",
                "timeline": "Day 19 – Day 35",
                "target_params": {"temperature": "22–25°C", "humidity": "75–80% RH", "light": "PPFD 350 µmol/m²/s", "ec_ph": "EC 1.8–2.2 mS/cm, pH 5.6–6.0"},
                "protocol": "Prune all laterals for first 6 nodes. Parthenocarpic fruit develops without pollination."
            },
            {
                "stage_number": 4,
                "stage_name": "Continuous Daily Morning Harvesting",
                "timeline": "Day 36 – Day 50",
                "target_params": {"length": "30–35 cm (English) / 12–15 cm (Persian)", "diameter": "3.5–4.5 cm"},
                "protocol": "Harvest daily in the morning when fruit is crisp and hydrated."
            },
            {
                "stage_number": 5,
                "stage_name": "Heat-Shrink Poly Film Sealing & Retail Supply",
                "timeline": "Day 51 – Day 55",
                "target_params": {"storage_temp": "10–12°C", "packaging": "Individual polyolefin shrink film", "shelf_life": "14–18 Days"},
                "protocol": "Individually shrink-wrap each fruit to prevent moisture loss. Distribute in 10kg cartons at ₹40–90/kg."
            }
        ]
    },
    "Kale": {
        "total_days": "45–60 Days",
        "system_type": "Nutrient Film Technique (NFT) / Vertical Towers",
        "summary": "Superfood cruciferous leafy green with continuous perpetual harvest capability.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Nursery Plug Germination",
                "timeline": "Day 1 – Day 5",
                "target_params": {"temperature": "18–22°C", "humidity": "85% RH", "light": "16h light", "ec_ph": "EC 0.8 mS/cm, pH 6.0"},
                "protocol": "Sow 2 seeds per plug in rockwool. Thin to strongest seedling on Day 5."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Vegetative Expansion",
                "timeline": "Day 6 – Day 16",
                "target_params": {"temperature": "18–20°C", "humidity": "65% RH", "light": "Strong blue spectrum LED", "ec_ph": "EC 1.2–1.5 mS/cm, pH 6.0"},
                "protocol": "Develop thick waxy cuticle and deep blue/green pigmentation."
            },
            {
                "stage_number": 3,
                "stage_name": "NFT Channel Transplant & Rosette Thickening",
                "timeline": "Day 17 – Day 38",
                "target_params": {"temperature": "16–20°C", "humidity": "60% RH", "light": "16h light", "ec_ph": "EC 1.8–2.4 mS/cm, pH 5.8–6.2"},
                "protocol": "Transplant into NFT channels at 25cm spacing. High nitrogen and sulfur boost glucosinolates."
            },
            {
                "stage_number": 4,
                "stage_name": "Perpetual Staggered Outer Leaf Harvest",
                "timeline": "Day 39 – Day 55",
                "target_params": {"leaf_length": "25–35 cm", "crinkling": "Deep savoy curling"},
                "protocol": "Snap lower mature leaves from the bottom up every 4–5 days while central growing apex continues upward growth."
            },
            {
                "stage_number": 5,
                "stage_name": "Hydro-Cooling, Bunch Banding & Wellness Delivery",
                "timeline": "Day 56 – Day 60",
                "target_params": {"storage_temp": "2–4°C", "packaging": "Banded 250g bunches in kraft sleeves", "shelf_life": "12–16 Days"},
                "protocol": "Hydro-cool to 3°C, band into 250g bunches. Supply to cold-pressed juice bars, organic retail & salad bars at ₹120–220/kg."
            }
        ]
    },
    "Mint": {
        "total_days": "30–45 Days",
        "system_type": "Deep Water Culture (DWC) / NFT Recirculating",
        "summary": "Vigorous perennial herb with continuous multi-mow commercial cycles.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Stem Cutting Rooting & Stolon Inoculation",
                "timeline": "Day 1 – Day 7",
                "target_params": {"temperature": "20–24°C", "humidity": "85% RH", "light": "16h light", "ec_ph": "EC 0.8 mS/cm, pH 6.0"},
                "protocol": "Root 8cm apical stem cuttings in aerated cloner. Profuse white roots form in 5–6 days."
            },
            {
                "stage_number": 2,
                "stage_name": "Transplant & Rapid Stolon Branching",
                "timeline": "Day 8 – Day 20",
                "target_params": {"temperature": "20–24°C", "humidity": "65% RH", "light": "16h light (PPFD 220 µmol/m²/s)", "ec_ph": "EC 1.4–1.8 mS/cm, pH 5.8–6.2"},
                "protocol": "Insert rooted plugs into NFT channels. High dissolved oxygen triggers rapid lateral runner shoots."
            },
            {
                "stage_number": 3,
                "stage_name": "Dense Canopy Foliage & Menthol Enrichment",
                "timeline": "Day 21 – Day 35",
                "target_params": {"temperature": "20–23°C", "humidity": "60% RH", "light": "High PPFD 300 µmol/m²/s", "ec_ph": "EC 1.8–2.2 mS/cm, pH 6.0"},
                "protocol": "Intense light stimulates menthol oil glands on leaf undersides. High transpiration requires daily nutrient top-up."
            },
            {
                "stage_number": 4,
                "stage_name": "Full Canopy Mow Harvest",
                "timeline": "Day 36 – Day 42",
                "target_params": {"cut_height": "5cm above channel collar", "aroma": "Pungent sweet menthol"},
                "protocol": "Mow top 20cm stems. Crown regenerates a full new harvest every 18–21 days."
            },
            {
                "stage_number": 5,
                "stage_name": "Breathable Packaging & Beverage Supply",
                "timeline": "Day 43 – Day 45",
                "target_params": {"storage_temp": "4–6°C", "packaging": "Vented polyethylene bags (100g/500g)", "shelf_life": "8–12 Days"},
                "protocol": "Pack in breathable moisture-resistant bags. Supply to cocktail lounges, juice bars & herbal tea blenders at ₹100–180/kg."
            }
        ]
    },
    "Microgreens": {
        "total_days": "10–15 Days",
        "system_type": "Vertical Multi-Tier Racks with Capillary Mats / Coco Pads",
        "summary": "Ultra-fast turnaround luxury garnish with extraordinary nutritional density.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "High-Density Tray Seeding & Blackout Weighting",
                "timeline": "Day 1 – Day 3",
                "target_params": {"temperature": "20–22°C", "humidity": "90% RH", "light": "Total darkness under 2kg stack weight", "ec_ph": "Pure RO water, pH 5.8"},
                "protocol": "Broadcast dense seed layer on food-grade hemp/cellulose mats. Stack trays with 2kg top weights to force uniform stem elongation."
            },
            {
                "stage_number": 2,
                "stage_name": "Blackout Dome & Chlorophyll Greening",
                "timeline": "Day 4 – Day 5",
                "target_params": {"temperature": "20–22°C", "humidity": "75% RH", "light": "Indirect ambient light", "ec_ph": "EC 0.6 mS/cm, pH 5.8"},
                "protocol": "Unstack trays. Expose to gentle light; pale yellow shoots turn vivid green/magenta in 24 hours."
            },
            {
                "stage_number": 3,
                "stage_name": "Vertical LED Photoperiod & Sub-Irrigation",
                "timeline": "Day 6 – Day 10",
                "target_params": {"temperature": "19–21°C", "humidity": "50–60% RH", "light": "18h vertical LED (PPFD 150 µmol/m²/s)", "ec_ph": "EC 0.8–1.0 mS/cm, pH 5.8"},
                "protocol": "Sub-irrigate via automated bottom flood trays. Cross-ventilation fans eliminate any fungal damping-off."
            },
            {
                "stage_number": 4,
                "stage_name": "True-Leaf Cut or Living Pad Harvesting",
                "timeline": "Day 10 – Day 14",
                "target_params": {"height": "5–8 cm", "stage": "Expanded cotyledons + first true leaf emerging"},
                "protocol": "Harvest with sterile ceramic knife 5mm above pad, or sell live with pad intact in clear clamshells."
            },
            {
                "stage_number": 5,
                "stage_name": "Tamper-Evident Clamshells & Michelin Delivery",
                "timeline": "Day 14 – Day 15",
                "target_params": {"storage_temp": "2–4°C", "packaging": "Clear vented PET 50g/100g punnets", "shelf_life": "10–14 Days"},
                "protocol": "Pack dry microgreens in clear clamshells with absorbent bottom pad. Express morning delivery to fine dining restaurants & luxury catering at ₹500–1,200/kg."
            }
        ]
    },
    "Coriander": {
        "total_days": "35–48 Days",
        "system_type": "Nutrient Film Technique (NFT) / Deep Water Culture (DWC)",
        "summary": "Essential culinary staple with high consumer turnover in everyday kitchens.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Split-Seed Sowing & Moist Germination",
                "timeline": "Day 1 – Day 7",
                "target_params": {"temperature": "18–20°C", "humidity": "85% RH", "light": "Darkness for 5 days", "ec_ph": "Pure RO water, pH 6.0"},
                "protocol": "Gently crush coriander seeds into halves. Sow in rockwool/perlite plugs. Seedlings emerge in 6–8 days."
            },
            {
                "stage_number": 2,
                "stage_name": "Nursery Rosette Formation",
                "timeline": "Day 8 – Day 18",
                "target_params": {"temperature": "18–21°C", "humidity": "65% RH", "light": "14h light", "ec_ph": "EC 1.0–1.2 mS/cm, pH 6.0"},
                "protocol": "Develop sturdy basal stems and feathery true leaves. Keep water cool to prevent bolting."
            },
            {
                "stage_number": 3,
                "stage_name": "NFT Channel Transplant & Heavy Foliage Growth",
                "timeline": "Day 19 – Day 35",
                "target_params": {"temperature": "17–21°C", "humidity": "60% RH", "light": "14h light (PPFD 220 µmol/m²/s)", "ec_ph": "EC 1.4–1.8 mS/cm, pH 5.8–6.2"},
                "protocol": "Maintain high nitrogen and micronutrient levels for deep green aroma. Strict temperature control below 22°C."
            },
            {
                "stage_number": 4,
                "stage_name": "Full Rosette Harvesting & Quality Grading",
                "timeline": "Day 36 – Day 45",
                "target_params": {"height": "20–25 cm", "color": "Lush emerald green without yellowing"},
                "protocol": "Harvest whole bunches with clean root cut or live root collar."
            },
            {
                "stage_number": 5,
                "stage_name": "Perforated Sleeves & Fresh Market Dispatch",
                "timeline": "Day 46 – Day 48",
                "target_params": {"storage_temp": "2–4°C", "packaging": "Micro-perforated conical poly sleeves", "shelf_life": "10–14 Days"},
                "protocol": "Hydro-cool, pack in vented bunches. Distribute to fresh grocery chains & daily wholesale markets at ₹80–160/kg."
            }
        ]
    },
    "Spirulina": {
        "total_days": "14–20 Days",
        "system_type": "Open Raceway Ponds with Paddlewheel Agitation / Closed Photobioreactors",
        "summary": "Blue-green microalgae superfood with 65%+ protein density and phycocyanin pigment.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Zarrouk Alkaline Medium Prep & Sterile Inoculation",
                "timeline": "Day 1 – Day 3",
                "target_params": {"temperature": "30–35°C", "pH": "9.0–10.5", "light": "Continuous 2500 lux", "medium": "High NaHCO3 sodium bicarbonate buffer"},
                "protocol": "Prepare sterile Zarrouk nutrient broth in nursery photobioreactor. Inoculate pure Arthrospira platensis mother culture."
            },
            {
                "stage_number": 2,
                "stage_name": "Raceway Scale-Up & Exponential Phototrophic Growth",
                "timeline": "Day 4 – Day 8",
                "target_params": {"temperature": "32–37°C", "pH": "9.5–10.2", "light": "Full solar / High PPFD LED", "paddle_speed": "25–30 cm/s flow velocity"},
                "protocol": "Transfer to open raceway pond at 15–20cm depth. Paddlewheel ensures uniform light exposure and prevents thermal stratification."
            },
            {
                "stage_number": 3,
                "stage_name": "Peak Optical Density & Harvesting Trigger",
                "timeline": "Day 9 – Day 14",
                "target_params": {"optical_density": "OD560 > 0.8", "secchi_depth": "2.0–2.5 cm", "biomass_density": "1.0–1.5 g/L dry equiv"},
                "protocol": "Trigger harvest when Secchi disk depth reaches 2.5cm. Pump culture through 30-micron inclined vibrating mesh screens."
            },
            {
                "stage_number": 4,
                "stage_name": "Biomass Dewatering & Vacuum Salt Wash",
                "timeline": "Day 14 – Day 16",
                "target_params": {"paste_moisture": "78–82%", "wash_water": "Pure demineralized RO water"},
                "protocol": "Filter paste on vacuum drum. Wash with RO water to remove residual carbonate salts down to food-grade standard."
            },
            {
                "stage_number": 5,
                "stage_name": "Low-Temp Solar / Spray Drying & Milling",
                "timeline": "Day 16 – Day 18",
                "target_params": {"drying_temp": "< 45°C (Preserves phycocyanin)", "final_moisture": "< 7.0%", "mesh_size": "100–120 Mesh"},
                "protocol": "Extrude into spaghetti noodles for low-temperature solar tunnel drying or spray dry. Pulverize in food-grade hammer mill."
            },
            {
                "stage_number": 6,
                "stage_name": "NABL Lab Quality Assay, Foil Packaging & B2B Sales",
                "timeline": "Day 18 – Day 20",
                "target_params": {"protein_assay": ">60% crude protein", "heavy_metals": "Pb < 0.2 ppm, As < 0.1 ppm", "packaging": "Multi-layer nitrogen-flushed foil pouch"},
                "protocol": "Conduct NABL test for microcystins and heavy metals. Seal in airtight 1kg/25kg bags with Digital Quality Assurance Certificate. Sell to nutraceutical brands at ₹650–1,200/kg."
            }
        ]
    },
    "Chlorella": {
        "total_days": "16–22 Days",
        "system_type": "Closed Tubular Glass Photobioreactor (PBR)",
        "summary": "Single-cell green microalgae with superior chlorophyll and cell-wall broken digestibility.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Sterile Media Formulation & Pure Culture Inoculation",
                "timeline": "Day 1 – Day 4",
                "target_params": {"temperature": "25–30°C", "pH": "6.8–7.5", "light": "PPFD 200 µmol/m²/s", "co2_injection": "1.5% CO2 gas enriched air"},
                "protocol": "Prepare sterilized BG-11 media. Inoculate pure Chlorella vulgaris in starter seed photobioreactors under HEPA filtration."
            },
            {
                "stage_number": 2,
                "stage_name": "Tubular Glass PBR Logarithmic Expansion",
                "timeline": "Day 5 – Day 10",
                "target_params": {"temperature": "27–32°C", "pH": "7.0–7.4", "light": "High solar exposure", "flow_rate": "0.8 m/s turbulent flow"},
                "protocol": "Circulate culture through glass tubular loops. Continuous dissolved oxygen degassing prevents oxygen toxicity."
            },
            {
                "stage_number": 3,
                "stage_name": "Industrial Disc-Stack Centrifuge Separation",
                "timeline": "Day 11 – Day 16",
                "target_params": {"cell_count": "> 2.5 x 10^7 cells/mL", "concentration": "100x concentrated slurry"},
                "protocol": "Continuous disc-stack centrifuge concentrates microalgae into a thick emerald green concentrated paste."
            },
            {
                "stage_number": 4,
                "stage_name": "High-Pressure Mechanical Cell-Wall Disruption",
                "timeline": "Day 17 – Day 19",
                "target_params": {"homogenizer_pressure": "800–1000 Bar", "cracking_rate": "> 85% broken cell wall"},
                "protocol": "Pass paste through high-pressure homogenizer to crack tough cellulose cell walls, boosting human bio-availability to >85%."
            },
            {
                "stage_number": 5,
                "stage_name": "Spray Drying, Hermetic Sealing & Export Handover",
                "timeline": "Day 20 – Day 22",
                "target_params": {"chlorophyll": "> 2500 mg/100g", "protein": "> 55%", "shelf_life": "24 Months"},
                "protocol": "Spray dry into ultra-fine powder. Vacuum seal in food-grade drums with oxygen scavengers. Supply to health supplement laboratories at ₹800–1,500/kg."
            }
        ]
    },
    "Oyster Mushroom": {
        "total_days": "30–40 Days",
        "system_type": "Indoor Climate-Controlled Hanging Bag Substrate System",
        "summary": "High-yield edible mushroom converting agricultural crop straw into culinary protein.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Substrate Chopping, Soaking & Thermal Pasteurization",
                "timeline": "Day 1 – Day 3",
                "target_params": {"substrate": "Paddy straw / Wheat straw / Sawdust (3–5cm)", "moisture": "65% RH", "pasteurization": "80°C hot water for 2 hours or steam"},
                "protocol": "Chop clean dry straw. Soak and pasteurize to eliminate competitor molds. Drain to squeeze-test standard (no dripping water)."
            },
            {
                "stage_number": 2,
                "stage_name": "Aseptic Grain Spawn Inoculation & Bag Packing",
                "timeline": "Day 4 – Day 5",
                "target_params": {"spawn_rate": "3–4% grain spawn by dry weight", "bag_size": "2kg Polypropylene (PP) bags with micro-filters"},
                "protocol": "Cool substrate to <28°C. Layer spawn evenly with straw in bags. Tie tightly and punch 10 needle ventilation holes."
            },
            {
                "stage_number": 3,
                "stage_name": "Spawn Run / Dark Mycelial Colonization",
                "timeline": "Day 6 – Day 22",
                "target_params": {"temperature": "24–26°C", "humidity": "75% RH", "light": "Total darkness", "co2": "High (> 3000 ppm)"},
                "protocol": "Hang bags in dark incubation room. White fungal mycelium rapidly spreads through entire straw substrate in 16–18 days."
            },
            {
                "stage_number": 4,
                "stage_name": "Fruiting Induction, Fresh Air & Pinheading",
                "timeline": "Day 23 – Day 28",
                "target_params": {"temperature": "18–22°C (Cold shock drop)", "humidity": "85–90% RH (Fine foggers)", "light": "12h diffuse light (500 lux)", "co2": "< 800 ppm (High fresh air)"},
                "protocol": "Cut 5cm slits on bags. Drop temperature by 4–5°C and introduce fresh air. Tiny pinheads emerge from slits within 72 hours."
            },
            {
                "stage_number": 5,
                "stage_name": "First Flush Cluster Harvesting & Trimming",
                "timeline": "Day 29 – Day 35",
                "target_params": {"harvest_stage": "Cap edges uncurled, before spores release", "cluster_yield": "400–600g per bag"},
                "protocol": "Grip cluster at base and twist off cleanly. Trim residual substrate straw with sharp knife."
            },
            {
                "stage_number": 6,
                "stage_name": "Perforated Packaging & Restaurant Distribution",
                "timeline": "Day 36 – Day 40",
                "target_params": {"storage_temp": "3–5°C", "packaging": "Vented paper trays with perforated wrap", "shelf_life": "6–8 Days"},
                "protocol": "Store in cold room (rest bags for Flush 2 and 3). Deliver fresh clusters to grocers, vegan meat startups & restaurants at ₹120–180/kg."
            }
        ]
    },
    "Shiitake": {
        "total_days": "75–90 Days",
        "system_type": "Hardwood Sawdust Block Cultivation in Clean Rooms",
        "summary": "Prized culinary and medicinal mushroom with rich savory umami and high lentinan content.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Hardwood Substrate Formulation & Autoclaving",
                "timeline": "Day 1 – Day 5",
                "target_params": {"mix": "80% Oak/broadleaf sawdust + 18% wheat bran + 2% gypsum", "moisture": "60%", "autoclave": "121°C at 15 PSI for 3 hours"},
                "protocol": "Mix substrate thoroughly, pack into filter-patch polypropylene bags, pressure sterilize in autoclave."
            },
            {
                "stage_number": 2,
                "stage_name": "Sterile Inoculation in Laminar Flow",
                "timeline": "Day 6 – Day 8",
                "target_params": {"environment": "ISO Class 5 Laminar Air Flow", "spawn": "Pure Lentinula edodes grain/sawdust spawn at 3%"},
                "protocol": "Cool substrate completely to 20°C. Inoculate under HEPA laminar airflow. Seal bags."
            },
            {
                "stage_number": 3,
                "stage_name": "Mycelium Colonization, Popcorn Bump & Browning Phase",
                "timeline": "Day 9 – Day 65",
                "target_params": {"temperature": "22–24°C", "humidity": "65–70% RH", "light": "Darkness for 45 days, then 12h light", "co2": "High"},
                "protocol": "Mycelium colonizes white (Day 1–30), forms popcorn-like mycelial bumps (Day 31–50), and oxidizes into a dark brown melanized protective rind (Day 51–65)."
            },
            {
                "stage_number": 4,
                "stage_name": "Cold Water Immersion Shock & Fruiting Trigger",
                "timeline": "Day 66 – Day 75",
                "target_params": {"soaking": "Strip plastic bag, submerge log in ice-cold water (10–12°C) for 12 hours", "fruiting_temp": "16–18°C", "humidity": "85–90% RH"},
                "protocol": "Cold shock triggers primordial formation across the brown log surface. Move to humid fruiting room."
            },
            {
                "stage_number": 5,
                "stage_name": "Donko Grade Mushroom Harvesting",
                "timeline": "Day 76 – Day 85",
                "target_params": {"cap_diameter": "5–8 cm", "cap_state": "Veil broken, thick convex fleshy cap (Donko grade)"},
                "protocol": "Cut stem flush with log surface using curved stainless knife. Grade for thick crackle-top caps."
            },
            {
                "stage_number": 6,
                "stage_name": "Fresh & Dehydrated Mushroom Market Supply",
                "timeline": "Day 86 – Day 90",
                "target_params": {"fresh_storage": "2–4°C in wood pulp cartons (14 days)", "dried_version": "Dehydrate at 50°C to 8% moisture (24 months shelf life)"},
                "protocol": "Distribute fresh to Japanese/Pan-Asian hospitality at ₹300–600/kg; dehydrate premium grade for dry umami retail at ₹2,000–3,500/kg."
            }
        ]
    },
    "Button Mushroom": {
        "total_days": "60–75 Days",
        "system_type": "Two-Phase Composted Trays / Shelf Beds with Casing Layer",
        "summary": "World's highest volume commercial mushroom grown on pasteurized compost beds.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Composting Phase I (Fermentation) & Phase II (Pasteurization)",
                "timeline": "Day 1 – Day 15",
                "target_params": {"compost_mix": "Wheat straw + poultry manure + gypsum", "phase2_temp": "60°C peak heat for 8 hours, conditioning at 48°C for 6 days"},
                "protocol": "Bulk composting produces nitrogen-rich, ammonia-free selective substrate for Agaricus bisporus."
            },
            {
                "stage_number": 2,
                "stage_name": "Spawning & Tray Colonization (Spawn Run)",
                "timeline": "Day 16 – Day 30",
                "target_params": {"temperature": "24–25°C compost temp", "humidity": "90% RH", "spawn_rate": "0.7% rye grain spawn", "co2": "> 4000 ppm"},
                "protocol": "Mix spawn thoroughly into compost beds. Cover with perforated paper. Mycelium permeates compost in 14 days."
            },
            {
                "stage_number": 3,
                "stage_name": "Casing Layer Application & Ruffling",
                "timeline": "Day 31 – Day 45",
                "target_params": {"casing_material": "Pasteurized peat moss + spent lime (pH 7.5)", "depth": "4 cm thickness", "temp": "24°C"},
                "protocol": "Apply moist casing layer over colonized compost. Ruffle casing on Day 40 to ensure uniform mycelial knotting."
            },
            {
                "stage_number": 4,
                "stage_name": "Cool Airing, Pinhead Initiation & Flush Emergence",
                "timeline": "Day 46 – Day 55",
                "target_params": {"air_temp": "16–18°C", "humidity": "85–88% RH", "co2": "Drop to 1000 ppm (Heavy fresh air venting)"},
                "protocol": "Heavy ventilation and temperature drop shock mycelium into forming millions of tiny pea-sized pinheads."
            },
            {
                "stage_number": 5,
                "stage_name": "Closed Button Harvesting (First Flush)",
                "timeline": "Day 56 – Day 65",
                "target_params": {"cap_size": "35–50 mm", "veil": "Completely closed tight veil beneath cap"},
                "protocol": "Hand-twist harvest mature white buttons. Cut root base with stainless knife. Rest 8 days for Flush 2 and 3."
            },
            {
                "stage_number": 6,
                "stage_name": "MAP Punnets & Wholesale Supermarket Distribution",
                "timeline": "Day 66 – Day 75",
                "target_params": {"storage_temp": "2–4°C", "packaging": "200g/400g sealed overwrapped punnets", "shelf_life": "7–10 Days"},
                "protocol": "Pack in automated punnet lines. Supply to national supermarket chains & pizza/canning processors at ₹110–170/kg."
            }
        ]
    },
    "Lion's Mane": {
        "total_days": "35–45 Days",
        "system_type": "Enriched Hardwood Sawdust Polypropylene Grow Bags",
        "summary": "Exotic gourmet and nootropic medicinal mushroom resembling white icicle pom-poms.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Supplemented Hardwood Substrate Sterilization",
                "timeline": "Day 1 – Day 4",
                "target_params": {"mix": "78% Oak/beech sawdust + 20% organic wheat bran + 2% gypsum", "moisture": "60%", "sterilization": "121°C for 2.5 hours"},
                "protocol": "Bag supplemented substrate in autoclavable gusseted bags with 0.2-micron filter patches."
            },
            {
                "stage_number": 2,
                "stage_name": "Pure Culture Inoculation",
                "timeline": "Day 5 – Day 6",
                "target_params": {"spawn": "Hericium erinaceus grain spawn at 4%", "environment": "HEPA laminar flow hood"},
                "protocol": "Inoculate sterile substrate under sterile air. Seal bags."
            },
            {
                "stage_number": 3,
                "stage_name": "Incubation & Rapid Mycelial Colonization",
                "timeline": "Day 7 – Day 22",
                "target_params": {"temperature": "22–24°C", "humidity": "70% RH", "light": "Total darkness", "co2": "High (> 2500 ppm)"},
                "protocol": "Mycelium spreads as a delicate wispy white web throughout substrate in 15–18 days."
            },
            {
                "stage_number": 4,
                "stage_name": "Slit Cutting & Icicle Spine Primordia Induction",
                "timeline": "Day 23 – Day 32",
                "target_params": {"temperature": "18–20°C", "humidity": "88–92% RH (Ultrasonic foggers)", "light": "12h diffuse light (800 lux)", "co2": "< 750 ppm (Continuous air exchange)"},
                "protocol": "Cut a single 5cm 'X' on bag face. Primordium pushes through slit and expands into a white snowball pom-pom."
            },
            {
                "stage_number": 5,
                "stage_name": "Pure White Snowball Harvesting",
                "timeline": "Day 33 – Day 40",
                "target_params": {"spine_length": "3–5 mm icicles", "color": "Brilliant pure white (harvest BEFORE any yellowing)"},
                "protocol": "Slice cleanly at base of fruit body. Handle gently to avoid bruising delicate spines."
            },
            {
                "stage_number": 6,
                "stage_name": "Breathable Clamshells & Nootropic Extraction Sales",
                "timeline": "Day 41 – Day 45",
                "target_params": {"fresh_storage": "2–4°C in cushioned vented clamshells (7–9 days)", "dried_nootropic": "Dehydrate at 40°C for hericenones extraction"},
                "protocol": "Distribute fresh to fine-dining chefs & vegan steak restaurants at ₹400–800/kg; dry for brain health nootropic supplement brands at ₹3,000–5,000/kg."
            }
        ]
    },
    "Milky Mushroom": {
        "total_days": "35–45 Days",
        "system_type": "Layered Straw Bags with Casing in Tropical Warm Rooms",
        "summary": "Robust tropical mushroom flourishing in 30–35°C heat with long natural shelf life.",
        "stages": [
            {
                "stage_number": 1,
                "stage_name": "Straw Chopping & Steam Pasteurization",
                "timeline": "Day 1 – Day 3",
                "target_params": {"substrate": "Dry paddy straw chopped to 3–5 cm", "pasteurization": "Boiling water at 80°C for 90 minutes", "moisture": "65%"},
                "protocol": "Pasteurize straw in drums. Drain on sanitized mesh tables."
            },
            {
                "stage_number": 2,
                "stage_name": "Layered Spawning & Bag Compaction",
                "timeline": "Day 4 – Day 5",
                "target_params": {"spawn": "Calocybe indica grain spawn at 4%", "bag": "Polythene bag (35x60cm)"},
                "protocol": "Layer straw and spawn alternately in 4 tiers. Compact firmly, tie top, and punch 12 ventilation pinholes."
            },
            {
                "stage_number": 3,
                "stage_name": "Warm Spawn Run Colonization",
                "timeline": "Day 6 – Day 20",
                "target_params": {"temperature": "28–32°C (Thrives in heat)", "humidity": "80% RH", "light": "Darkness"},
                "protocol": "Incubate in warm room. Vigorous white mycelium fully embeds substrate in 14–16 days."
            },
            {
                "stage_number": 4,
                "stage_name": "Bag Cutting, Casing Layer & Pinhead Formation",
                "timeline": "Day 21 – Day 30",
                "target_params": {"casing": "2–3cm sterilized red garden soil + chalk (pH 8.0)", "temperature": "30–35°C", "humidity": "85–90% RH", "light": "Diffuse ambient daylight"},
                "protocol": "Cut bag top open, apply moist 3cm casing layer. Light daily water misting triggers dense pinhead clusters in 8–10 days."
            },
            {
                "stage_number": 5,
                "stage_name": "Large White Fleshy Mushroom Harvesting",
                "timeline": "Day 31 – Day 40",
                "target_params": {"cap_size": "8–15 cm umbrella cap", "single_weight": "150–300g per mushroom"},
                "protocol": "Twist off large brilliant white mushrooms before cap margin rolls upward. Brush casing soil cleanly."
            },
            {
                "stage_number": 6,
                "stage_name": "Perforated Polybags & Tropical Market Supply",
                "timeline": "Day 41 – Day 45",
                "target_params": {"storage": "Remarkable 4–5 days at ambient room temperature (25°C), 15 days at 4°C", "packaging": "Perforated polybags (250g/500g)"},
                "protocol": "Pack in standard vented bags. Supply to tropical grocers, curry cloud kitchens & South Asian foodservice at ₹140–220/kg."
            }
        ]
    }
}
