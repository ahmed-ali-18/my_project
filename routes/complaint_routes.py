import os

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from ai.complaint_classifier import classify_complaint
from models import Complaint, db


complaint_bp = Blueprint("complaints", __name__)


CATEGORIES = [
    "Road Issues",
    "Garbage Management",
    "Water Supply",
    "Street Lighting",
    "Drainage Issues",
]


def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@complaint_bp.route("/")
def index():
    return render_template("index.html")


@complaint_bp.route("/citizen/dashboard")
@login_required
def citizen_dashboard():
    if current_user.is_admin():
        return redirect(url_for("admin.admin_dashboard"))

    complaints_query = Complaint.query.filter_by(user_id=current_user.id).order_by(
        Complaint.created_at.desc()
    )
    complaints = complaints_query.all()
    total = len(complaints)
    pending = len([c for c in complaints if c.status == "pending"])
    resolved = len([c for c in complaints if c.status == "resolved"])
    delayed = len([c for c in complaints if c.flagged])

    return render_template(
        "citizen_dashboard.html",
        complaints=complaints,
        total=total,
        pending=pending,
        resolved=resolved,
        delayed=delayed,
    )


@complaint_bp.route("/complaints/new", methods=["GET", "POST"])
@login_required
def new_complaint():
    if current_user.is_admin():
        flash("Admins cannot submit complaints.", "warning")
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        area = request.form.get("area", "").strip()
        category = request.form.get("category") or None
        auto_classify = request.form.get("auto_classify") == "on"
        image = request.files.get("image")

        if not title or not description or not area:
            flash("Title, description, and area are required.", "danger")
            return render_template("complaint_form.html", categories=CATEGORIES)

        image_filename = None
        if image and image.filename:
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                image.save(image_path)
                image_filename = filename
            else:
                flash("Invalid image type. Only JPG/PNG allowed.", "danger")
                return render_template("complaint_form.html", categories=CATEGORIES)

        if auto_classify or not category:
            predicted, _prob = classify_complaint(title, description)
            category = predicted

        complaint = Complaint(
            title=title,
            description=description,
            area=area,
            category=category,
            status="pending",
            user_id=current_user.id,
            image_filename=image_filename,
        )
        db.session.add(complaint)
        db.session.commit()
        flash("Complaint submitted successfully.", "success")
        return redirect(url_for("complaints.citizen_dashboard"))

    return render_template("complaint_form.html", categories=CATEGORIES)


@complaint_bp.route("/complaints/history")
@login_required
def complaint_history():
    if current_user.is_admin():
        return redirect(url_for("admin.admin_dashboard"))
    complaints = Complaint.query.filter_by(user_id=current_user.id).order_by(
        Complaint.created_at.desc()
    )
    return render_template("complaint_history.html", complaints=complaints)

