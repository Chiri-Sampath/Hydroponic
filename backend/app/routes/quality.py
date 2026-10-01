"""
AgriSmart AI — Quality & Batch Routes
=======================================
Endpoints for:
  - Cultivation Batch CRUD
  - Lab Report Upload & OCR Extraction
  - Individual Test Result Recording
  - Digital Quality Passport Generation & QR Code
  - Public Read-Only Passport Verification
"""

import os
from datetime import datetime, timezone, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models.project import Project
from ..models.cultivation import Product
from ..models.quality import (
    Batch, QualityTest, ProductTestRequirement,
    LabReport, TestResult, QualityPassport
)
from ..services.ocr_service import extract_lab_report_data
from ..services.passport_service import compile_passport_summary, generate_qr_code_base64
from ..utils.security import generate_batch_code, generate_share_token, allowed_upload_file
from ..utils.auth_decorators import require_active_user, require_ownership

quality_bp = Blueprint("quality", __name__)


class BatchCreateSchema(Schema):
    product_id = fields.Int(required=True)
    start_date = fields.Date(load_default=None)
    expected_harvest_date = fields.Date(load_default=None)
    area_sqm = fields.Float(load_default=None)
    notes = fields.Str(load_default="")


@quality_bp.route("/user/passports", methods=["GET"])
@jwt_required()
@require_active_user
def list_user_passports():
    """GET /api/quality/user/passports - List all batches and quality passports for current user"""
    user_id = int(get_jwt_identity())
    batches = Batch.query.join(Project).filter(
        Project.user_id == user_id,
        Project.status == "active"
    ).order_by(Batch.created_at.desc()).all()

    passports_data = []
    for b in batches:
        passport = b.quality_passport
        passports_data.append({
            "batch_id": b.id,
            "batch_code": b.batch_code,
            "project_id": b.project_id,
            "project_name": b.project.name if b.project else "N/A",
            "product_name": b.product.common_name if b.product else "N/A",
            "ecosystem": b.product.method.display_name if (b.product and b.product.method) else "Soil-Free",
            "status": b.status,
            "start_date": b.start_date.isoformat() if b.start_date else None,
            "actual_harvest_date": b.actual_harvest_date.isoformat() if b.actual_harvest_date else None,
            "has_passport": passport is not None,
            "share_token": passport.share_token if passport else None,
            "qr_code_image": passport.qr_data if passport else None,
            "overall_status": passport.summary.get("overall_quality_status", "Compliant") if (passport and passport.summary) else "In Progress",
            "tests_passed": passport.summary.get("tests_passed_count", 0) if (passport and passport.summary) else b.test_results.filter_by(pass_fail="pass").count(),
            "tests_total": passport.summary.get("tests_conducted_count", 0) if (passport and passport.summary) else b.test_results.count(),
        })

    return jsonify({
        "success": True,
        "data": passports_data,
        "meta": {"count": len(passports_data)}
    }), 200


@quality_bp.route("/project/<int:project_id>/batches", methods=["GET"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def list_project_batches(project_id: int):
    """GET /api/quality/project/<id>/batches - List batches for a project"""
    batches = Batch.query.filter_by(project_id=project_id).order_by(Batch.created_at.desc()).all()
    return jsonify({
        "success": True,
        "data": [
            {
                "id": b.id,
                "batch_code": b.batch_code,
                "product_id": b.product_id,
                "product_name": b.product.common_name if b.product else "N/A",
                "method_display": b.product.method.display_name if (b.product and b.product.method) else "Soil-Free",
                "cultivation_plan": b.product.cultivation_plan if b.product else {},
                "varieties": b.product.varieties if b.product else [],
                "status": b.status,
                "start_date": b.start_date.isoformat() if b.start_date else None,
                "expected_harvest_date": b.expected_harvest_date.isoformat() if b.expected_harvest_date else None,
                "actual_harvest_date": b.actual_harvest_date.isoformat() if b.actual_harvest_date else None,
                "area_sqm": float(b.area_sqm) if b.area_sqm is not None else None,
                "actual_yield_kg": float(b.actual_yield_kg) if b.actual_yield_kg is not None else None,
                "notes": b.notes or "",
                "reports_count": b.lab_reports.count(),
                "tests_count": b.test_results.count(),
                "has_passport": b.quality_passport is not None,
            }
            for b in batches
        ]
    }), 200


@quality_bp.route("/project/<int:project_id>/batches", methods=["POST"])
@jwt_required()
@require_active_user
@require_ownership(Project, id_param="project_id")
def create_batch(project_id: int):
    """POST /api/quality/project/<id>/batches - Create a new cultivation batch"""
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"success": False, "error": "Project not found"}), 404

    schema = BatchCreateSchema()
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"success": False, "error": "Validation error", "details": e.messages}), 422

    product = db.session.get(Product, data["product_id"])
    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    batch_code = generate_batch_code(prefix=product.common_name[:3].upper())

    batch = Batch(
        project_id=project.id,
        product_id=product.id,
        batch_code=batch_code,
        status="planned",
        start_date=data.get("start_date") or date.today(),
        expected_harvest_date=data.get("expected_harvest_date"),
        area_sqm=data.get("area_sqm"),
        notes=data.get("notes", "").strip(),
    )
    db.session.add(batch)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Batch {batch.batch_code} created successfully",
        "data": {
            "id": batch.id,
            "batch_code": batch.batch_code,
            "product_name": product.common_name,
            "status": batch.status,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
        }
    }), 201


@quality_bp.route("/batches/<int:batch_id>", methods=["GET"])
@jwt_required()
@require_active_user
def get_batch_detail(batch_id: int):
    """GET /api/quality/batches/<id> - Get full batch information with test results"""
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404

    user_id = int(get_jwt_identity())
    if batch.project.user_id != user_id:
        return jsonify({"success": False, "error": "Access denied"}), 403

    p = batch.product
    return jsonify({
        "success": True,
        "data": {
            "id": batch.id,
            "batch_code": batch.batch_code,
            "project_id": batch.project_id,
            "product_id": batch.product_id,
            "product_name": p.common_name if p else "N/A",
            "method": p.method.display_name if (p and p.method) else "Soil-Free",
            "status": batch.status,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "expected_harvest_date": batch.expected_harvest_date.isoformat() if batch.expected_harvest_date else None,
            "actual_harvest_date": batch.actual_harvest_date.isoformat() if batch.actual_harvest_date else None,
            "area_sqm": float(batch.area_sqm) if batch.area_sqm else None,
            "actual_yield_kg": float(batch.actual_yield_kg) if batch.actual_yield_kg is not None else None,
            "notes": batch.notes,
            "lab_reports": [
                {
                    "id": lr.id,
                    "filename": lr.original_filename,
                    "ocr_status": lr.ocr_status,
                    "created_at": lr.created_at.isoformat() if lr.created_at else None,
                }
                for lr in batch.lab_reports
            ],
            "test_results": [
                {
                    "id": tr.id,
                    "test_name": tr.test_name_as_reported,
                    "result_value": tr.result_value,
                    "specification_limit": tr.specification_limit,
                    "pass_fail": tr.pass_fail,
                    "verified": not tr.needs_manual_verification,
                }
                for tr in batch.test_results
            ],
            "has_passport": batch.quality_passport is not None,
            "passport_share_token": batch.quality_passport.share_token if batch.quality_passport else None,
        }
    }), 200


@quality_bp.route("/batches/<int:batch_id>", methods=["PUT", "PATCH"])
@jwt_required()
@require_active_user
def update_batch(batch_id: int):
    """PUT /api/quality/batches/<id> - Update batch stage, status, yield, or notes"""
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404

    user_id = int(get_jwt_identity())
    if batch.project.user_id != user_id:
        return jsonify({"success": False, "error": "Access denied"}), 403

    payload = request.get_json(force=True) or {}
    
    if "status" in payload:
        batch.status = payload["status"]
    if "notes" in payload:
        batch.notes = payload["notes"]
    if "actual_yield_kg" in payload:
        batch.actual_yield_kg = float(payload["actual_yield_kg"]) if payload["actual_yield_kg"] is not None else None
    if "actual_harvest_date" in payload:
        if payload["actual_harvest_date"]:
            try:
                batch.actual_harvest_date = datetime.strptime(payload["actual_harvest_date"], "%Y-%m-%d").date()
            except ValueError:
                pass
        else:
            batch.actual_harvest_date = None
    if "start_date" in payload:
        if payload["start_date"]:
            try:
                batch.start_date = datetime.strptime(payload["start_date"], "%Y-%m-%d").date()
            except ValueError:
                pass

    db.session.commit()
    return jsonify({
        "success": True,
        "message": f"Batch {batch.batch_code} updated successfully",
        "data": {
            "id": batch.id,
            "batch_code": batch.batch_code,
            "status": batch.status,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "actual_harvest_date": batch.actual_harvest_date.isoformat() if batch.actual_harvest_date else None,
            "actual_yield_kg": float(batch.actual_yield_kg) if batch.actual_yield_kg is not None else None,
            "notes": batch.notes,
        }
    }), 200


@quality_bp.route("/batches/<int:batch_id>/report", methods=["POST"])
@jwt_required()
@require_active_user
def upload_lab_report(batch_id: int):
    """
    POST /api/quality/batches/<id>/report
    -------------------------------------
    Upload a PDF or image lab test report. Automatically extracts test results
    using OCR and saves them as test results on the batch.
    """
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404

    user_id = int(get_jwt_identity())
    if batch.project.user_id != user_id:
        return jsonify({"success": False, "error": "Access denied"}), 403

    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded in 'file' field"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Selected file has no filename"}), 400

    allowed_exts = current_app.config.get("ALLOWED_UPLOAD_EXTENSIONS", {"pdf", "png", "jpg", "jpeg"})
    if not allowed_upload_file(file.filename, allowed_exts):
        return jsonify({"success": False, "error": f"File type not allowed. Supported: {', '.join(allowed_exts)}"}), 400

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)

    orig_name = secure_filename(file.filename)
    safe_name = f"batch_{batch.id}_{int(datetime.now(timezone.utc).timestamp())}_{orig_name}"
    save_path = os.path.join(upload_folder, safe_name)
    file.save(save_path)

    # Run OCR Extraction
    extracted = extract_lab_report_data(save_path)

    report = LabReport(
        batch_id=batch.id,
        uploaded_by_user_id=user_id,
        original_filename=orig_name,
        storage_path=save_path,
        file_type=os.path.splitext(orig_name)[1].replace(".", "").lower(),
        file_size_bytes=os.path.getsize(save_path) if os.path.exists(save_path) else 0,
        ocr_status="complete",
        ocr_raw_text=extracted.get("raw_text", ""),
        ocr_extracted=extracted,
        ocr_confidence_flags=extracted.get("confidence_flags", []),
    )
    db.session.add(report)
    db.session.flush()

    # Save extracted test results to batch
    for t in extracted.get("tests", []):
        tr = TestResult(
            batch_id=batch.id,
            lab_report_id=report.id,
            test_name_as_reported=t.get("test_name"),
            result_value=t.get("result_value"),
            specification_limit=t.get("specification_limit"),
            pass_fail=t.get("pass_fail", "pass"),
            needs_manual_verification=t.get("confidence") == "low",
        )
        db.session.add(tr)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"Lab report uploaded and parsed successfully. {len(extracted.get('tests', []))} test parameters extracted.",
        "data": {
            "report_id": report.id,
            "filename": report.original_filename,
            "extracted_tests": extracted.get("tests", []),
            "confidence_flags": extracted.get("confidence_flags", []),
        }
    }), 201


@quality_bp.route("/batches/<int:batch_id>/passport", methods=["GET", "POST"])
@jwt_required()
@require_active_user
def get_or_create_passport(batch_id: int):
    """
    GET / POST /api/quality/batches/<id>/passport
    --------------------------------------------
    Generate or fetch the Digital Quality Passport with QR code for a batch.
    """
    batch = db.session.get(Batch, batch_id)
    if not batch:
        return jsonify({"success": False, "error": "Batch not found"}), 404

    user_id = int(get_jwt_identity())
    if batch.project.user_id != user_id:
        return jsonify({"success": False, "error": "Access denied"}), 403

    summary = compile_passport_summary(batch)

    passport = batch.quality_passport
    if not passport:
        token = generate_share_token()
        # Generate QR code pointing to public verification page
        frontend_url = current_app.config.get("FRONTEND_URL", "http://localhost:5500")
        verify_url = f"{frontend_url}/pages/user/quality-passport.html?token={token}"
        qr_base64 = generate_qr_code_base64(verify_url)

        passport = QualityPassport(
            batch_id=batch.id,
            share_token=token,
            is_shared=True,
            qr_data=qr_base64,
            summary=summary,
        )
        db.session.add(passport)
        db.session.commit()
    else:
        # Update summary snapshot
        passport.summary = summary
        db.session.commit()

    return jsonify({
        "success": True,
        "data": {
            "passport_id": passport.id,
            "batch_code": batch.batch_code,
            "share_token": passport.share_token,
            "qr_code_image": passport.qr_data,
            "passport_data": summary,
        }
    }), 200


@quality_bp.route("/passport/<string:share_token>", methods=["GET"])
def get_public_passport(share_token: str):
    """
    GET /api/quality/passport/<share_token>
    ---------------------------------------
    Public read-only verification endpoint. Zero authentication required.
    Allows buyers, retailers, and end-consumers to verify quality data.
    """
    passport = QualityPassport.query.filter_by(share_token=share_token).first()
    if not passport:
        if share_token.lower() in ["demo", "sample", "preview"]:
            demo_passport = {
                "batch_code": "LETT-2026-001-DEMO",
                "product_name": "Butterhead Lettuce (Hydroponics NFT)",
                "method": "Hydroponics (Nutrient Film Technique)",
                "producer_project": "Bengaluru Precision CEA Farm #1",
                "harvest_date": "2026-09-25",
                "overall_quality_status": "GRADE A / 100% FSSAI COMPLIANT",
                "tests_conducted_count": 5,
                "tests_passed_count": 5,
                "disclaimer": "This is a cryptographically verified Digital Quality Assurance Certificate generated by AgriSmart AI OCR Verification Network.",
                "test_results": [
                    {"test_name": "E. coli / Total Coliforms", "result_value": "Absent / Not Detected (< 10 CFU/g)", "specification_limit": "FSSAI Max: Absent in 25g", "pass_fail": "pass"},
                    {"test_name": "Salmonella spp.", "result_value": "Absent in 25g", "specification_limit": "FSSAI: Nil", "pass_fail": "pass"},
                    {"test_name": "Lead (Pb) Heavy Metal", "result_value": "0.012 mg/kg", "specification_limit": "FSSAI Max: 0.1 mg/kg", "pass_fail": "pass"},
                    {"test_name": "Cadmium (Cd) Heavy Metal", "result_value": "0.004 mg/kg", "specification_limit": "FSSAI Max: 0.05 mg/kg", "pass_fail": "pass"},
                    {"test_name": "Multi-Residue Pesticide Screen (250+ active compounds)", "result_value": "Not Detected (< 0.01 mg/kg)", "specification_limit": "MRL Zero Tolerance", "pass_fail": "pass"}
                ]
            }
            return jsonify({
                "success": True,
                "data": {
                    "batch_code": demo_passport["batch_code"],
                    "qr_code_image": None,
                    "passport": demo_passport,
                },
                "meta": {
                    "verified_by": "AgriSmart AI Digital Quality Network (Demo Mode)",
                    "token": share_token,
                }
            }), 200
        return jsonify({"success": False, "error": "Invalid or expired quality assurance verification token"}), 404

    return jsonify({
        "success": True,
        "data": {
            "batch_code": passport.batch.batch_code,
            "qr_code_image": passport.qr_data,
            "passport": passport.summary or compile_passport_summary(passport.batch),
        },
        "meta": {
            "verified_by": "AgriSmart AI Digital Quality Network",
            "token": share_token,
        }
    }), 200
