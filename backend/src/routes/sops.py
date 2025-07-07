from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, SOP, SOPRead
from src.routes.auth import login_required, admin_required
from datetime import datetime

sops_bp = Blueprint("sops", __name__)

@sops_bp.route("", methods=["GET"])
@login_required
def get_sops():
    try:
        sops = SOP.query.order_by(SOP.created_at.desc()).all()
        result = []
        for sop in sops:
            sop_dict = sop.to_dict()
            sop_dict["creator"] = {
                "id": sop.creator.id,
                "first_name": sop.creator.first_name,
                "last_name": sop.creator.last_name,
            }
            result.append(sop_dict)
        return jsonify({"sops": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sops_bp.route("", methods=["POST"])
@admin_required
def create_sop():
    try:
        data = request.get_json()

        required_fields = ["title", "file_url"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        sop = SOP(
            title=data["title"],
            description=data.get("description"),
            file_url=data["file_url"],
            category=data.get("category"),
            tags=data.get("tags"),
            created_by=session["user_id"],
        )

        db.session.add(sop)
        db.session.commit()

        return jsonify({"message": "SOP created successfully", "sop": sop.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sops_bp.route("/<int:sop_id>", methods=["PUT"])
@admin_required
def update_sop(sop_id):
    try:
        sop = SOP.query.get_or_404(sop_id)
        data = request.get_json()

        if "title" in data:
            sop.title = data["title"]
        if "description" in data:
            sop.description = data["description"]
        if "file_url" in data:
            sop.file_url = data["file_url"]
        if "category" in data:
            sop.category = data["category"]
        if "tags" in data:
            sop.tags = data["tags"]

        db.session.commit()

        return jsonify({"message": "SOP updated successfully", "sop": sop.to_dict()}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sops_bp.route("/<int:sop_id>", methods=["DELETE"])
@admin_required
def delete_sop(sop_id):
    try:
        sop = SOP.query.get_or_404(sop_id)

        db.session.delete(sop)
        db.session.commit()

        return jsonify({"message": "SOP deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sops_bp.route("/<int:sop_id>/read", methods=["POST"])
@login_required
def mark_sop_read(sop_id):
    try:
        user_id = session["user_id"]
        sop = SOP.query.get_or_404(sop_id)

        read_record = SOPRead.query.filter_by(
            user_id=user_id, sop_id=sop_id
        ).first()

        if read_record:
            return jsonify({"error": "SOP already marked as read"}), 400

        read_record = SOPRead(
            user_id=user_id,
            sop_id=sop_id,
            read_at=datetime.utcnow(),
        )
        db.session.add(read_record)
        db.session.commit()

        return jsonify({"message": "SOP marked as read"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@sops_bp.route("/read_status", methods=["GET"])
@login_required
def get_sop_read_status():
    try:
        user_id = session["user_id"]
        read_records = SOPRead.query.filter_by(user_id=user_id).all()
        return jsonify({"read_sops": [record.to_dict() for record in read_records]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

