"""
AgriSmart AI — Quality, Lab & Batch Models
===========================================
Tables:
  batches, quality_tests, product_test_requirements,
  test_results, lab_reports, quality_passports,
  laboratories, lab_capabilities, lab_test_mappings
"""

from datetime import datetime, timezone
from ..extensions import db


class Batch(db.Model):
    """
    A cultivation batch linked to a project.
    Forms the root of the Digital Quality Passport.
    status: planned | in_progress | harvested | sold | archived
    """

    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    batch_code = db.Column(db.String(100), unique=True, nullable=False, index=True)
    status = db.Column(
        db.String(50),
        default="planned",
    )
    start_date = db.Column(db.Date, nullable=True)
    expected_harvest_date = db.Column(db.Date, nullable=True)
    actual_harvest_date = db.Column(db.Date, nullable=True)
    area_sqm = db.Column(db.Numeric(10, 2), nullable=True)
    actual_yield_kg = db.Column(db.Numeric(10, 3), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    project = db.relationship("Project", back_populates="batches")
    product = db.relationship("Product")
    test_results = db.relationship("TestResult", back_populates="batch", lazy="dynamic",
                                    cascade="all, delete-orphan")
    lab_reports = db.relationship("LabReport", back_populates="batch", lazy="dynamic",
                                   cascade="all, delete-orphan")
    quality_passport = db.relationship("QualityPassport", back_populates="batch",
                                        uselist=False, cascade="all, delete-orphan")


class QualityTest(db.Model):
    """
    Master list of quality tests (managed by Admin).
    test_category: legal | buyer | voluntary | recommended
    """

    __tablename__ = "quality_tests"

    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(300), nullable=False)
    test_category = db.Column(
        db.String(50),
        nullable=False,
    )
    purpose = db.Column(db.Text, nullable=True)
    sample_type = db.Column(db.String(200), nullable=True)          # fresh, dried, extract
    standard_reference = db.Column(db.String(300), nullable=True)   # e.g. FSSAI, ISO, AGMARK
    applicable_jurisdiction = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    data_source = db.Column(db.String(300), nullable=True)
    data_version = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    product_requirements = db.relationship("ProductTestRequirement", back_populates="quality_test",
                                            lazy="dynamic")
    lab_mappings = db.relationship("LabTestMapping", back_populates="quality_test", lazy="dynamic")


class ProductTestRequirement(db.Model):
    """
    Maps a specific product to a specific required/recommended quality test.
    is_required: True = mandatory; False = recommended/optional
    """

    __tablename__ = "product_test_requirements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    quality_test_id = db.Column(db.Integer, db.ForeignKey("quality_tests.id"), nullable=False)
    is_required = db.Column(db.Boolean, default=True)
    applicable_markets = db.Column(db.String(300), nullable=True)   # e.g. "Export, Nutraceutical"
    buyer_requirement = db.Column(db.String(300), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship("Product", back_populates="product_test_requirements")
    quality_test = db.relationship("QualityTest", back_populates="product_requirements")


class Laboratory(db.Model):
    """
    Laboratory registry (Admin managed).
    All information sourced and verified by admin.
    The application does NOT claim to certify lab accreditation automatically.
    """

    __tablename__ = "laboratories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    short_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), default="India")
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(254), nullable=True)
    website = db.Column(db.String(500), nullable=True)
    accreditation = db.Column(db.String(200), nullable=True)     # e.g. "NABL", "ISO 17025"
    accreditation_verified = db.Column(db.Boolean, default=False)
    typical_turnaround_days_min = db.Column(db.Integer, nullable=True)
    typical_turnaround_days_max = db.Column(db.Integer, nullable=True)
    indicative_cost_notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    data_source = db.Column(db.String(300), nullable=True)
    data_verified_at = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    capabilities = db.relationship("LabCapability", back_populates="laboratory", lazy="dynamic",
                                    cascade="all, delete-orphan")
    test_mappings = db.relationship("LabTestMapping", back_populates="laboratory", lazy="dynamic",
                                     cascade="all, delete-orphan")


class LabCapability(db.Model):
    """General capability categories of a laboratory."""

    __tablename__ = "lab_capabilities"

    id = db.Column(db.Integer, primary_key=True)
    laboratory_id = db.Column(db.Integer, db.ForeignKey("laboratories.id"), nullable=False, index=True)
    capability_area = db.Column(db.String(300), nullable=False)   # e.g. "Microbiology", "Heavy Metals"
    sample_types_accepted = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    laboratory = db.relationship("Laboratory", back_populates="capabilities")


class LabTestMapping(db.Model):
    """Maps a specific quality test to a lab that can perform it."""

    __tablename__ = "lab_test_mappings"

    id = db.Column(db.Integer, primary_key=True)
    laboratory_id = db.Column(db.Integer, db.ForeignKey("laboratories.id"), nullable=False, index=True)
    quality_test_id = db.Column(db.Integer, db.ForeignKey("quality_tests.id"), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)  # admin verified lab can do this test
    indicative_cost_inr = db.Column(db.Numeric(8, 2), nullable=True)
    turnaround_days = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    laboratory = db.relationship("Laboratory", back_populates="test_mappings")
    quality_test = db.relationship("QualityTest", back_populates="lab_mappings")


class LabReport(db.Model):
    """
    Uploaded lab report (PDF or image) for a batch.
    OCR extraction results stored as JSON.
    ocr_status: pending | complete | failed | manual_review
    """

    __tablename__ = "lab_reports"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    laboratory_id = db.Column(db.Integer, db.ForeignKey("laboratories.id"), nullable=True)
    uploaded_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(500), nullable=False)
    storage_path = db.Column(db.String(1000), nullable=False)      # server-side safe path
    file_type = db.Column(db.String(10), nullable=True)            # pdf / png / jpg
    file_size_bytes = db.Column(db.Integer, nullable=True)
    ocr_status = db.Column(
        db.String(50),
        default="pending",
    )
    ocr_raw_text = db.Column(db.Text, nullable=True)
    ocr_extracted = db.Column(db.JSON, nullable=True)              # structured extracted fields
    ocr_confidence_flags = db.Column(db.JSON, nullable=True)       # low-confidence field names
    report_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    batch = db.relationship("Batch", back_populates="lab_reports")
    test_results = db.relationship("TestResult", back_populates="lab_report", lazy="dynamic")


class TestResult(db.Model):
    """
    Individual test result extracted from a lab report for a batch.
    pass_fail: pass | fail | inconclusive | not_applicable
    """

    __tablename__ = "test_results"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), nullable=False, index=True)
    lab_report_id = db.Column(db.Integer, db.ForeignKey("lab_reports.id"), nullable=True)
    quality_test_id = db.Column(db.Integer, db.ForeignKey("quality_tests.id"), nullable=True)
    test_name_as_reported = db.Column(db.String(300), nullable=True)  # OCR-extracted name
    result_value = db.Column(db.String(200), nullable=True)
    result_unit = db.Column(db.String(100), nullable=True)
    specification_limit = db.Column(db.String(200), nullable=True)
    pass_fail = db.Column(
        db.String(50),
        nullable=True,
    )
    needs_manual_verification = db.Column(db.Boolean, default=False)
    test_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    batch = db.relationship("Batch", back_populates="test_results")
    lab_report = db.relationship("LabReport", back_populates="test_results")


class QualityPassport(db.Model):
    """
    Digital quality passport for a batch.
    Aggregates batch, inputs, tests, lab reports, packaging, and buyer.
    share_token: random token for read-only sharing with buyers.
    """

    __tablename__ = "quality_passports"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id"), unique=True, nullable=False)
    share_token = db.Column(db.String(64), unique=True, nullable=True, index=True)
    is_shared = db.Column(db.Boolean, default=False)
    qr_data = db.Column(db.Text, nullable=True)                   # QR-encoded URL or data string
    summary = db.Column(db.JSON, nullable=True)                   # Snapshot of key pass/fail results
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    batch = db.relationship("Batch", back_populates="quality_passport")
