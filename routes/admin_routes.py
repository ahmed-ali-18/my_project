from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from sqlalchemy import func

from models import Complaint, User, db


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    from functools import wraps
    from flask import abort

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)

    return wrapper


def update_delay_flags():
    threshold_minutes = current_app.config.get("DELAY_THRESHOLD_MINUTES", 2)
    try:
        threshold_minutes = int(threshold_minutes)
    except (TypeError, ValueError):
        threshold_minutes = 2
    complaints = Complaint.query.all()
    changed = False
    for c in complaints:
        old_flag = c.flagged
        c.update_flag(threshold_minutes)
        if c.flagged != old_flag:
            changed = True
    if changed:
        db.session.commit()


@admin_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():
    update_delay_flags()

    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="pending").count()
    in_progress = Complaint.query.filter_by(status="in_progress").count()
    resolved = Complaint.query.filter_by(status="resolved").count()
    delayed = Complaint.query.filter_by(flagged=True).count()

    if delayed > 0:
        flash(
            f"Notification: {delayed} complaint(s) have exceeded the resolution time and are flagged as delayed. Please resolve them.",
            "warning",
        )

    return render_template(
        "admin_dashboard.html",
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        delayed=delayed,
    )


@admin_bp.route("/complaints")
@login_required
@admin_required
def list_complaints():
    update_delay_flags()

    status = request.args.get("status")
    area = request.args.get("area")
    category = request.args.get("category")
    delayed_count = Complaint.query.filter_by(flagged=True).count()

    if delayed_count > 0:
        flash(
            f"Notification: {delayed_count} delayed complaint(s) need attention (not resolved within the time limit).",
            "warning",
        )

    query = Complaint.query.order_by(Complaint.created_at.desc())
    if status:
        query = query.filter_by(status=status)
    if area:
        query = query.filter(Complaint.area.ilike(f"%{area}%"))
    if category:
        query = query.filter_by(category=category)

    complaints = query.all()

    return render_template(
        "admin_complaints.html",
        complaints=complaints,
        filter_status=status,
        filter_area=area,
        filter_category=category,
        delayed_count=delayed_count,
    )


@admin_bp.route("/complaints/<int:complaint_id>/update", methods=["POST"])
@login_required
@admin_required
def update_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    new_status = request.form.get("status")
    if new_status not in {"pending", "in_progress", "resolved"}:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin.list_complaints"))

    complaint.status = new_status
    if new_status == "resolved":
        complaint.resolved_at = datetime.utcnow()

    threshold = current_app.config.get("DELAY_THRESHOLD_MINUTES", 2)
    try:
        threshold = int(threshold)
    except (TypeError, ValueError):
        threshold = 2
    complaint.update_flag(threshold)
    db.session.commit()
    flash("Complaint updated.", "success")
    return redirect(url_for("admin.list_complaints"))


@admin_bp.route("/delayed")
@login_required
@admin_required
def delayed_complaints():
    update_delay_flags()
    complaints = Complaint.query.filter_by(flagged=True).order_by(
        Complaint.created_at.desc()
    ).all()
    delayed_count = len(complaints)
    return render_template(
        "admin_complaints.html",
        complaints=complaints,
        filter_status="delayed",
        filter_area=None,
        filter_category=None,
        delayed_count=delayed_count,
    )


@admin_bp.route("/analytics")
@login_required
@admin_required
def analytics_page():
    return render_template("admin_analytics.html")


@admin_bp.route("/analytics-data")
@login_required
@admin_required
def analytics_data():
    update_delay_flags()

    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status="pending").count()
    in_progress = Complaint.query.filter_by(status="in_progress").count()
    resolved = Complaint.query.filter_by(status="resolved").count()
    delayed = Complaint.query.filter_by(flagged=True).count()

    by_area = (
        db.session.query(Complaint.area, func.count(Complaint.id))
        .group_by(Complaint.area)
        .all()
    )

    by_category = (
        db.session.query(Complaint.category, func.count(Complaint.id))
        .group_by(Complaint.category)
        .all()
    )

    resolution_times = []
    resolved_complaints = Complaint.query.filter_by(status="resolved").all()
    for c in resolved_complaints:
        if c.resolved_at and c.created_at:
            delta = c.resolved_at - c.created_at
            resolution_times.append(delta.total_seconds() / 86400.0)

    avg_resolution = (
        sum(resolution_times) / len(resolution_times) if resolution_times else 0
    )

    return jsonify(
        {
            "counts": {
                "total": total,
                "pending": pending,
                "in_progress": in_progress,
                "resolved": resolved,
                "delayed": delayed,
            },
            "by_area": [{"area": a, "count": count} for a, count in by_area],
            "by_category": [
                {"category": c or "Uncategorized", "count": count}
                for c, count in by_category
            ],
            "resolution": {
                "average_days": avg_resolution,
                "samples": resolution_times,
            },
        }
    )

