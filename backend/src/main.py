import os
import sys
# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db, User
from src.routes.auth import auth_bp
from src.routes.time_logs import time_logs_bp
from src.routes.eod_reports import eod_reports_bp
from src.routes.announcements import announcements_bp
from src.routes.trainings import trainings_bp
from src.routes.sops import sops_bp
from src.routes.leave_requests import leave_requests_bp
from src.routes.users import users_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'turma-labs-secret-key-2024'

# Enable CORS for all routes
CORS(app, supports_credentials=True)

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(time_logs_bp, url_prefix='/api/time-logs')
app.register_blueprint(eod_reports_bp, url_prefix='/api/eod-reports')
app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
app.register_blueprint(trainings_bp, url_prefix='/api/trainings')
app.register_blueprint(sops_bp, url_prefix='/api/sops')
app.register_blueprint(leave_requests_bp, url_prefix='/api/leave-requests')
app.register_blueprint(users_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user():
    """Create default admin user if it doesn't exist"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@turmalabs.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')  # Default password - should be changed
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created: username=admin, password=admin123")

with app.app_context():
    db.create_all()
    create_admin_user()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


