from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Announcement
from src.routes.auth import login_required, admin_required
from datetime import datetime

announcements_bp = Blueprint('announcements', __name__)

@announcements_bp.route('', methods=['GET'])
@login_required
def get_announcements():
    try:
        # Get all announcements, ordered by pinned first, then by creation date
        announcements = Announcement.query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.created_at.desc()
        ).all()
        
        result = []
        for announcement in announcements:
            announcement_dict = announcement.to_dict()
            announcement_dict['creator'] = {
                'id': announcement.creator.id,
                'first_name': announcement.creator.first_name,
                'last_name': announcement.creator.last_name
            }
            result.append(announcement_dict)
        
        return jsonify({'announcements': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('', methods=['POST'])
@admin_required
def create_announcement():
    try:
        data = request.get_json()
        
        required_fields = ['title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        announcement = Announcement(
            title=data['title'],
            content=data['content'],
            is_pinned=data.get('is_pinned', False),
            created_by=session['user_id']
        )
        
        db.session.add(announcement)
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement created successfully',
            'announcement': announcement.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/<int:announcement_id>', methods=['PUT'])
@admin_required
def update_announcement(announcement_id):
    try:
        announcement = Announcement.query.get_or_404(announcement_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'title' in data:
            announcement.title = data['title']
        if 'content' in data:
            announcement.content = data['content']
        if 'is_pinned' in data:
            announcement.is_pinned = data['is_pinned']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Announcement updated successfully',
            'announcement': announcement.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/<int:announcement_id>', methods=['DELETE'])
@admin_required
def delete_announcement(announcement_id):
    try:
        announcement = Announcement.query.get_or_404(announcement_id)
        
        db.session.delete(announcement)
        db.session.commit()
        
        return jsonify({'message': 'Announcement deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@announcements_bp.route('/recent', methods=['GET'])
@login_required
def get_recent_announcements():
    try:
        # Get the 3 most recent announcements for dashboard preview
        announcements = Announcement.query.order_by(
            Announcement.is_pinned.desc(),
            Announcement.created_at.desc()
        ).limit(3).all()
        
        result = []
        for announcement in announcements:
            announcement_dict = announcement.to_dict()
            announcement_dict['creator'] = {
                'id': announcement.creator.id,
                'first_name': announcement.creator.first_name,
                'last_name': announcement.creator.last_name
            }
            result.append(announcement_dict)
        
        return jsonify({'announcements': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

