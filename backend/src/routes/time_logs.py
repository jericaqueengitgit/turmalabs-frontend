from flask import Blueprint, request, jsonify, session, Response
from src.models.user import db, User, TimeLog
from src.routes.auth import login_required, admin_required
from datetime import datetime, date
from sqlalchemy import func
import csv
import io

time_logs_bp = Blueprint('time_logs', __name__)

@time_logs_bp.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    try:
        user_id = session['user_id']
        today = date.today()
        
        # Check if user already clocked in today
        existing_log = TimeLog.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if existing_log and existing_log.clock_in:
            return jsonify({'error': 'Already clocked in today'}), 400
        
        if existing_log:
            # Update existing log
            existing_log.clock_in = datetime.utcnow()
            existing_log.clock_out = None
            existing_log.total_hours = None
        else:
            # Create new log
            time_log = TimeLog(
                user_id=user_id,
                date=today,
                clock_in=datetime.utcnow()
            )
            db.session.add(time_log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Clocked in successfully',
            'clock_in': datetime.utcnow().isoformat()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@time_logs_bp.route('/clock-out', methods=['POST'])
@login_required
def clock_out():
    try:
        user_id = session['user_id']
        today = date.today()
        
        # Find today's time log
        time_log = TimeLog.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if not time_log or not time_log.clock_in:
            return jsonify({'error': 'Must clock in first'}), 400
        
        if time_log.clock_out:
            return jsonify({'error': 'Already clocked out today'}), 400
        
        # Update clock out time
        clock_out_time = datetime.utcnow()
        time_log.clock_out = clock_out_time
        
        # Calculate total hours
        time_diff = clock_out_time - time_log.clock_in
        total_hours = time_diff.total_seconds() / 3600
        time_log.total_hours = round(total_hours, 2)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Clocked out successfully',
            'clock_out': clock_out_time.isoformat(),
            'total_hours': time_log.total_hours
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@time_logs_bp.route('/today', methods=['GET'])
@login_required
def get_today_time_log():
    try:
        user_id = session['user_id']
        today = date.today()
        
        time_log = TimeLog.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if time_log:
            return jsonify({'time_log': time_log.to_dict()}), 200
        else:
            return jsonify({'time_log': None}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@time_logs_bp.route('', methods=['GET'])
@login_required
def get_time_logs():
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        # Build query
        query = TimeLog.query
        
        # If not admin, only show own logs
        if user.role != 'admin':
            query = query.filter_by(user_id=user_id)
        
        # Apply filters
        if request.args.get('user_id') and user.role == 'admin':
            query = query.filter_by(user_id=request.args.get('user_id'))
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            query = query.filter(TimeLog.date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            query = query.filter(TimeLog.date <= end_date)
        
        # Order by date descending
        time_logs = query.order_by(TimeLog.date.desc()).all()
        
        # Include user information for admin view
        result = []
        for log in time_logs:
            log_dict = log.to_dict()
            if user.role == 'admin':
                log_dict['user'] = {
                    'id': log.user.id,
                    'username': log.user.username,
                    'first_name': log.user.first_name,
                    'last_name': log.user.last_name
                }
            result.append(log_dict)
        
        return jsonify({'time_logs': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@time_logs_bp.route('/export', methods=['GET'])
@admin_required
def export_time_logs():
    try:
        # Build query with same filters as get_time_logs
        query = TimeLog.query
        
        # Apply filters
        if request.args.get('user_id'):
            query = query.filter_by(user_id=request.args.get('user_id'))
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            query = query.filter(TimeLog.date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            query = query.filter(TimeLog.date <= end_date)
        
        # Order by date descending
        time_logs = query.order_by(TimeLog.date.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Employee', 'Clock In', 'Clock Out', 'Total Hours'])
        
        # Write data
        for log in time_logs:
            writer.writerow([
                log.date.strftime('%Y-%m-%d'),
                f"{log.user.first_name} {log.user.last_name}",
                log.clock_in.strftime('%H:%M:%S') if log.clock_in else '',
                log.clock_out.strftime('%H:%M:%S') if log.clock_out else '',
                log.total_hours or ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=time_logs.csv'}
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@time_logs_bp.route('/summary', methods=['GET'])
@admin_required
def get_time_logs_summary():
    try:
        # Get summary statistics
        total_hours_today = db.session.query(func.sum(TimeLog.total_hours)).filter(
            TimeLog.date == date.today()
        ).scalar() or 0
        
        active_users_today = db.session.query(func.count(TimeLog.id)).filter(
            TimeLog.date == date.today(),
            TimeLog.clock_in.isnot(None)
        ).scalar() or 0
        
        clocked_in_now = db.session.query(func.count(TimeLog.id)).filter(
            TimeLog.date == date.today(),
            TimeLog.clock_in.isnot(None),
            TimeLog.clock_out.is_(None)
        ).scalar() or 0
        
        return jsonify({
            'total_hours_today': round(total_hours_today, 2),
            'active_users_today': active_users_today,
            'clocked_in_now': clocked_in_now
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

