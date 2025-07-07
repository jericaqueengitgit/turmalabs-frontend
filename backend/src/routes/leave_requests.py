from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, LeaveRequest
from src.routes.auth import login_required, admin_required
from datetime import datetime, date

leave_requests_bp = Blueprint("leave_requests", __name__)

@leave_requests_bp.route("", methods=["POST"])
@login_required
def submit_leave_request():
    try:
        user_id = session["user_id"]
        data = request.get_json()

        required_fields = ["start_date", "end_date", "reason"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

        if start_date > end_date:
            return jsonify({"error": "Start date cannot be after end date"}), 400

        leave_request = LeaveRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            reason=data["reason"],
            status="pending",
        )

        db.session.add(leave_request)
        db.session.commit()

        return jsonify(
            {
                "message": "Leave request submitted successfully",
                "request": leave_request.to_dict(),
            }
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@leave_requests_bp.route("", methods=["GET"])
@login_required
def get_leave_requests():
    try:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        query = LeaveRequest.query

        if user.role != "admin":
            query = query.filter_by(user_id=user_id)

        # Apply filters
        if request.args.get("status"):
            query = query.filter_by(status=request.args.get("status"))
        if request.args.get("user_id") and user.role == "admin":
            query = query.filter_by(user_id=request.args.get("user_id"))

        leave_requests = query.order_by(LeaveRequest.created_at.desc()).all()

        result = []
        for req in leave_requests:
            req_dict = req.to_dict()
            req_dict["user"] = {
                "id": req.user.id,
                "first_name": req.user.first_name,
                "last_name": req.user.last_name,
            }
            if req.reviewer:
                req_dict["reviewer"] = {
                    "id": req.reviewer.id,
                    "first_name": req.reviewer.first_name,
                    "last_name": req.reviewer.last_name,
                }
            result.append(req_dict)

        return jsonify({"leave_requests": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@leave_requests_bp.route("/<int:request_id>", methods=["PUT"])
@admin_required
def update_leave_request(request_id):
    try:
        leave_request = LeaveRequest.query.get_or_404(request_id)
        data = request.get_json()

        if "status" in data:
            leave_request.status = data["status"]
            leave_request.reviewed_at = datetime.utcnow()
            leave_request.reviewed_by = session["user_id"]
        if "admin_notes" in data:
            leave_request.admin_notes = data["admin_notes"]

        db.session.commit()

        return jsonify(
            {
                "message": "Leave request updated successfully",
                "request": leave_request.to_dict(),
            }
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

