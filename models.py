from datetime import datetime, timedelta

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="citizen")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaints = db.relationship("Complaint", back_populates="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == "admin"


class Complaint(db.Model):
    __tablename__ = "complaints"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=True, index=True)
    area = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    flagged = db.Column(db.Boolean, default=False, index=True)
    image_filename = db.Column(db.String(200), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="complaints")

    def mark_resolved(self) -> None:
        self.status = "resolved"
        self.resolved_at = datetime.utcnow()

    def compute_is_delayed(self, threshold_minutes: int = 2) -> bool:
        # Resolved complaints are never shown as delayed; notification is only for open ones
        if self.status == "resolved":
            return False
        if self.created_at is None:
            return False
        try:
            mins = int(threshold_minutes) if threshold_minutes is not None else 2
        except (TypeError, ValueError):
            mins = 2
        threshold = timedelta(minutes=mins)
        now = datetime.utcnow()
        return (now - self.created_at) > threshold

    def update_flag(self, threshold_minutes: int = 2) -> None:
        self.flagged = self.compute_is_delayed(threshold_minutes)

