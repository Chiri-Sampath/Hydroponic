"""
AgriSmart AI — User, Role & RBAC Models
==========================================
Tables: users, roles, permissions, role_permissions, audit_logs
"""

from datetime import datetime, timezone
from ..extensions import db


# ── Association table: many-to-many Role <-> Permission ─────────────────────
role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


class Role(db.Model):
    """User roles: general_user | buyer | admin"""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)           # general_user / buyer / admin
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    permissions = db.relationship("Permission", secondary=role_permissions, lazy="subquery",
                                  backref=db.backref("roles", lazy=True))
    users = db.relationship("User", back_populates="role", lazy="dynamic")

    def __repr__(self):
        return f"<Role {self.name}>"


class Permission(db.Model):
    """Fine-grained permissions (e.g. 'project:create', 'admin:user_manage')"""

    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Permission {self.code}>"


class User(db.Model):
    """
    Platform users.
    status: active | suspended | deactivated | pending_verification
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False, index=True)
    status = db.Column(
        db.Enum("active", "suspended", "deactivated", "pending_verification"),
        nullable=False,
        default="active",
    )
    email_verified = db.Column(db.Boolean, default=False)
    password_reset_token = db.Column(db.String(255), nullable=True)
    password_reset_expires = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role = db.relationship("Role", back_populates="users")
    profile = db.relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    projects = db.relationship("Project", back_populates="user", lazy="dynamic", cascade="all, delete-orphan")
    buyer_profile = db.relationship("BuyerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    audit_logs = db.relationship("AuditLog", back_populates="user", lazy="dynamic")

    def has_permission(self, permission_code: str) -> bool:
        """Check if this user's role has the given permission code."""
        return any(p.code == permission_code for p in self.role.permissions)

    def is_active(self) -> bool:
        return self.status == "active"

    def __repr__(self):
        return f"<User {self.email} [{self.role.name}]>"


class UserProfile(db.Model):
    """Extended profile for General User / Buyer."""

    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    organization = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="profile")


class AuditLog(db.Model):
    """
    Immutable audit trail for sensitive operations.
    Written on: login, logout, admin actions, role changes, status changes.
    """

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)     # e.g. 'user.login', 'admin.user.suspend'
    target_type = db.Column(db.String(100), nullable=True) # e.g. 'User', 'Project'
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)            # extra structured info
    ip_address = db.Column(db.String(45), nullable=True)   # IPv4/IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by user_id={self.user_id}>"
