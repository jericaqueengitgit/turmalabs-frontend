from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Training, TrainingProgress
from src.routes.auth import login_required, admin_required
from datetime import datetime

trainings_bp = Blueprint("trainings", __name__)

@trainings_bp.route("", methods=["GET"])
@login_required
def get_trainings():
    try:
        trainings = Training.query.order_by(Training.created_at.desc()).all()
        result = []
        for training in trainings:
            training_dict = training.to_dict()
            training_dict["creator"] = {
                "id": training.creator.id,
                "first_name": training.creator.first_name,
                "last_name": training.creator.last_name,
            }
            result.append(training_dict)
        return jsonify({"trainings": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("", methods=["POST"])
@admin_required
def create_training():
    try:
        data = request.get_json()

        required_fields = ["title"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        training = Training(
            title=data["title"],
            description=data.get("description"),
            url=data.get("url"),
            file_url=data.get("file_url"),
            video_url=data.get("video_url"),
            category=data.get("category"),
            skill_level=data.get("skill_level"),
            tags=data.get("tags"),
            created_by=session["user_id"],
        )

        db.session.add(training)
        db.session.commit()

        return jsonify(
            {"message": "Training created successfully", "training": training.to_dict()}
        ), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("/<int:training_id>", methods=["PUT"])
@admin_required
def update_training(training_id):
    try:
        training = Training.query.get_or_404(training_id)
        data = request.get_json()

        if "title" in data:
            training.title = data["title"]
        if "description" in data:
            training.description = data["description"]
        if "url" in data:
            training.url = data["url"]
        if "file_url" in data:
            training.file_url = data["file_url"]
        if "video_url" in data:
            training.video_url = data["video_url"]
        if "category" in data:
            training.category = data["category"]
        if "skill_level" in data:
            training.skill_level = data["skill_level"]
        if "tags" in data:
            training.tags = data["tags"]

        db.session.commit()

        return jsonify(
            {"message": "Training updated successfully", "training": training.to_dict()}
        ), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("/<int:training_id>", methods=["DELETE"])
@admin_required
def delete_training(training_id):
    try:
        training = Training.query.get_or_404(training_id)

        db.session.delete(training)
        db.session.commit()

        return jsonify({"message": "Training deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("/<int:training_id>/complete", methods=["POST"])
@login_required
def mark_training_complete(training_id):
    try:
        user_id = session["user_id"]
        training = Training.query.get_or_404(training_id)

        progress = TrainingProgress.query.filter_by(
            user_id=user_id, training_id=training_id
        ).first()

        if progress:
            if progress.completed:
                return jsonify({"error": "Training already marked as complete"}), 400
            progress.completed = True
            progress.completed_at = datetime.utcnow()
        else:
            progress = TrainingProgress(
                user_id=user_id,
                training_id=training_id,
                completed=True,
                completed_at=datetime.utcnow(),
            )
            db.session.add(progress)

        db.session.commit()

        return jsonify({"message": "Training marked as complete"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("/progress", methods=["GET"])
@login_required
def get_training_progress():
    try:
        user_id = session["user_id"]
        progress_records = TrainingProgress.query.filter_by(user_id=user_id).all()
        return jsonify(
            {"progress": [record.to_dict() for record in progress_records]}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@trainings_bp.route("/user_progress/<int:user_id>", methods=["GET"])
@admin_required
def get_user_training_progress(user_id):
    try:
        user = User.query.get_or_404(user_id)
        progress_records = TrainingProgress.query.filter_by(user_id=user_id).all()
        return jsonify(
            {"progress": [record.to_dict() for record in progress_records]}
        ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@trainings_bp.route("/bulk-import", methods=["POST"])
@admin_required
def bulk_import_trainings():
    try:
        data = request.get_json()
        trainings_data = data.get("trainings", [])
        
        if not trainings_data:
            return jsonify({"error": "No training data provided"}), 400
        
        created_count = 0
        for training_data in trainings_data:
            # Convert tags list to JSON string
            tags_str = None
            if training_data.get("tags"):
                import json
                tags_str = json.dumps(training_data["tags"])
            
            training = Training(
                title=training_data["title"],
                description=training_data.get("description"),
                url=training_data.get("url"),
                category=training_data.get("category"),
                skill_level=training_data.get("skillLevel"),  # Note: camelCase from JSON
                tags=tags_str,
                created_by=session["user_id"],
            )
            
            db.session.add(training)
            created_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully imported {created_count} trainings"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

