from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Admin
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    admin = Admin.query.filter_by(email=data['email']).first()

    if not admin or not admin.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Update last login
    admin.last_login = datetime.utcnow()
    db.session.commit()

    # Create JWT token
    access_token = create_access_token(identity=admin.id)

    return jsonify({
        'access_token': access_token,
        'admin': admin.to_dict()
    }), 200


@admin_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_admin():
    """Get current admin user info"""
    admin_id = get_jwt_identity()
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    return jsonify(admin.to_dict()), 200


@admin_bp.route('/create', methods=['POST'])
def create_admin():
    """Create a new admin user (for initial setup - should be protected in production)"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    # Check if admin already exists
    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Admin already exists'}), 400

    admin = Admin(
        email=data['email'],
        name=data.get('name')
    )
    admin.set_password(data['password'])

    db.session.add(admin)
    db.session.commit()

    return jsonify({
        'message': 'Admin created successfully',
        'admin': admin.to_dict()
    }), 201


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics"""
    from models import Customer, Call
    from sqlalchemy import func

    total_customers = Customer.query.count()
    active_customers = Customer.query.filter_by(subscription_status='active').count()
    trial_customers = Customer.query.filter_by(subscription_status='trial').count()

    total_calls = Call.query.count()
    calls_today = Call.query.filter(
        func.date(Call.created_at) == func.current_date()
    ).count()

    # Average call duration
    avg_duration = db.session.query(func.avg(Call.duration_seconds)).scalar() or 0

    return jsonify({
        'customers': {
            'total': total_customers,
            'active': active_customers,
            'trial': trial_customers
        },
        'calls': {
            'total': total_calls,
            'today': calls_today,
            'avg_duration_seconds': round(avg_duration, 2)
        }
    }), 200
