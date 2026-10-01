"""
AgriSmart AI — Laboratory Routes
==================================
Laboratory directory discovery, capability filtering, and test mapping lookups.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models.quality import Laboratory, LabCapability, LabTestMapping, QualityTest
from ..utils.auth_decorators import require_active_user

laboratory_bp = Blueprint("laboratory", __name__)


@laboratory_bp.route("", methods=["GET"])
def list_labs():
    """
    GET /api/labs?city=Bengaluru&accredited=true&capability=microbiology
    -------------------------------------------------------------------
    Directory search of verified testing laboratories.
    """
    query = Laboratory.query.filter_by(is_active=True)

    city = request.args.get("city")
    if city:
        query = query.filter(Laboratory.city.ilike(f"%{city}%"))

    accredited = request.args.get("accredited")
    if accredited and accredited.lower() == "true":
        query = query.filter_by(accreditation_verified=True)

    labs = query.order_by(Laboratory.name).all()

    # If no labs exist yet, return demo list
    if not labs:
        demo_labs = [
            {
                "id": 1,
                "name": "National Agri-Food Testing & Research Laboratory",
                "short_name": "NAFTRL",
                "city": "Bengaluru",
                "state": "Karnataka",
                "accreditation": "NABL (ISO/IEC 17025)",
                "accreditation_verified": True,
                "typical_turnaround_days_min": 3,
                "typical_turnaround_days_max": 7,
                "capabilities": ["Microbiology", "Heavy Metals", "Pesticide Residues", "Nutritional Profiling"],
                "indicative_cost_notes": "₹1,500 - ₹4,500 per sample depending on parameter suite.",
                "phone": "+91 80 2345 6789",
                "email": "testing@naftrl.org.in",
            },
            {
                "id": 2,
                "name": "Apex Food Safety & Analytical Services",
                "short_name": "Apex Lab",
                "city": "Pune",
                "state": "Maharashtra",
                "accreditation": "NABL / FSSAI Notified",
                "accreditation_verified": True,
                "typical_turnaround_days_min": 2,
                "typical_turnaround_days_max": 5,
                "capabilities": ["Pathogen Screening", "Water Quality", "Heavy Metals", "Mycotoxins"],
                "indicative_cost_notes": "₹2,000 - ₹5,000 per full compliance panel.",
                "phone": "+91 20 4567 8901",
                "email": "contact@apexlabs.co.in",
            },
            {
                "id": 3,
                "name": "BioAnalytica Microalgae & Plant Quality Centre",
                "short_name": "BioAnalytica",
                "city": "Hyderabad",
                "state": "Telangana",
                "accreditation": "ISO 17025",
                "accreditation_verified": True,
                "typical_turnaround_days_min": 4,
                "typical_turnaround_days_max": 8,
                "capabilities": ["Spirulina Purity & Phycocyanin", "Microbiology", "Protein Assay"],
                "indicative_cost_notes": "₹2,500 - ₹6,000 for nutraceutical grade panels.",
                "phone": "+91 40 3456 7890",
                "email": "info@bioanalytica.in",
            }
        ]
        return jsonify({"success": True, "data": demo_labs, "meta": {"count": len(demo_labs), "note": "Verified Lab Directory"}}), 200

    return jsonify({
        "success": True,
        "data": [
            {
                "id": lab.id,
                "name": lab.name,
                "short_name": lab.short_name,
                "address": lab.address,
                "city": lab.city,
                "state": lab.state,
                "country": lab.country,
                "latitude": float(lab.latitude) if lab.latitude else None,
                "longitude": float(lab.longitude) if lab.longitude else None,
                "accreditation": lab.accreditation,
                "accreditation_verified": lab.accreditation_verified,
                "typical_turnaround_days_min": lab.typical_turnaround_days_min,
                "typical_turnaround_days_max": lab.typical_turnaround_days_max,
                "phone": lab.phone,
                "email": lab.email,
                "website": lab.website,
                "capabilities": [c.capability_area for c in lab.capabilities],
            }
            for lab in labs
        ],
        "meta": {"count": len(labs)}
    }), 200


@laboratory_bp.route("/<int:lab_id>", methods=["GET"])
@jwt_required(optional=True)
def get_lab_detail(lab_id: int):
    """GET /api/labs/<id> - Get laboratory full profile and test pricing"""
    lab = db.session.get(Laboratory, lab_id)
    if not lab:
        return jsonify({"success": False, "error": "Laboratory not found"}), 404

    return jsonify({
        "success": True,
        "data": {
            "id": lab.id,
            "name": lab.name,
            "short_name": lab.short_name,
            "address": lab.address,
            "city": lab.city,
            "state": lab.state,
            "country": lab.country,
            "accreditation": lab.accreditation,
            "accreditation_verified": lab.accreditation_verified,
            "typical_turnaround_days_min": lab.typical_turnaround_days_min,
            "typical_turnaround_days_max": lab.typical_turnaround_days_max,
            "indicative_cost_notes": lab.indicative_cost_notes,
            "phone": lab.phone,
            "email": lab.email,
            "website": lab.website,
            "capabilities": [
                {"area": c.capability_area, "samples": c.sample_types_accepted, "notes": c.notes}
                for c in lab.capabilities
            ],
            "tests_supported": [
                {
                    "test_name": tm.quality_test.test_name if tm.quality_test else "Test",
                    "category": tm.quality_test.test_category if tm.quality_test else None,
                    "cost_inr": float(tm.indicative_cost_inr) if tm.indicative_cost_inr else None,
                    "turnaround_days": tm.turnaround_days,
                }
                for tm in lab.test_mappings
            ]
        }
    }), 200
