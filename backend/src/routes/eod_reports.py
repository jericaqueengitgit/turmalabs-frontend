from flask import Blueprint, request, jsonify, session, Response
from src.models.user import db, User, EODReport
from src.routes.auth import login_required, admin_required
from datetime import datetime, date
import csv
import io

eod_reports_bp = Blueprint('eod_reports', __name__)

@eod_reports_bp.route('', methods=['POST'])
@login_required
def submit_eod_report():
    try:
        user_id = session['user_id']
        data = request.get_json()
        
        required_fields = ['tasks_completed']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        today = date.today()
        
        # Check if report already exists for today
        existing_report = EODReport.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if existing_report:
            # Update existing report
            existing_report.tasks_completed = data['tasks_completed']
            existing_report.blockers = data.get('blockers', '')
            existing_report.issues = data.get('issues', '')
            existing_report.support_needed = data.get('support_needed', '')
            existing_report.created_at = datetime.utcnow()
        else:
            # Create new report
            report = EODReport(
                user_id=user_id,
                date=today,
                tasks_completed=data['tasks_completed'],
                blockers=data.get('blockers', ''),
                issues=data.get('issues', ''),
                support_needed=data.get('support_needed', '')
            )
            db.session.add(report)
        
        db.session.commit()
        
        return jsonify({
            'message': 'EOD report submitted successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@eod_reports_bp.route('/today', methods=['GET'])
@login_required
def get_today_eod_report():
    try:
        user_id = session['user_id']
        today = date.today()
        
        report = EODReport.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if report:
            return jsonify({'eod_report': report.to_dict()}), 200
        else:
            return jsonify({'eod_report': None}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@eod_reports_bp.route('', methods=['GET'])
@login_required
def get_eod_reports():
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        # Build query
        query = EODReport.query
        
        # If not admin, only show own reports
        if user.role != 'admin':
            query = query.filter_by(user_id=user_id)
        
        # Apply filters
        if request.args.get('user_id') and user.role == 'admin':
            query = query.filter_by(user_id=request.args.get('user_id'))
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            query = query.filter(EODReport.date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            query = query.filter(EODReport.date <= end_date)
        
        # Order by date descending
        reports = query.order_by(EODReport.date.desc()).all()
        
        # Include user information for admin view
        result = []
        for report in reports:
            report_dict = report.to_dict()
            if user.role == 'admin':
                report_dict['user'] = {
                    'id': report.user.id,
                    'username': report.user.username,
                    'first_name': report.user.first_name,
                    'last_name': report.user.last_name
                }
            result.append(report_dict)
        
        return jsonify({'eod_reports': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@eod_reports_bp.route('/export', methods=['GET'])
@admin_required
def export_eod_reports():
    try:
        # Build query with same filters as get_eod_reports
        query = EODReport.query
        
        # Apply filters
        if request.args.get('user_id'):
            query = query.filter_by(user_id=request.args.get('user_id'))
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            query = query.filter(EODReport.date >= start_date)
        
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            query = query.filter(EODReport.date <= end_date)
        
        # Order by date descending
        reports = query.order_by(EODReport.date.desc()).all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Employee', 'Tasks Completed', 'Blockers', 'Issues', 'Support Needed'])
        
        # Write data
        for report in reports:
            writer.writerow([
                report.date.strftime('%Y-%m-%d'),
                f"{report.user.first_name} {report.user.last_name}",
                report.tasks_completed,
                report.blockers or '',
                report.issues or '',
                report.support_needed or ''
            ])
        
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=eod_reports.csv'}
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@eod_reports_bp.route('/<int:report_id>', methods=['GET'])
@admin_required
def get_eod_report(report_id):
    try:
        report = EODReport.query.get_or_404(report_id)
        report_dict = report.to_dict()
        report_dict['user'] = {
            'id': report.user.id,
            'username': report.user.username,
            'first_name': report.user.first_name,
            'last_name': report.user.last_name
        }
        
        return jsonify({'eod_report': report_dict}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

