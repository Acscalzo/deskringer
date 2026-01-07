"""
Customer Portal API routes
These routes are for customers to access their own data via the customer portal
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, Customer, Call, CallLog
from datetime import datetime

customer_portal_bp = Blueprint('customer_portal', __name__)

@customer_portal_bp.route('/login', methods=['POST'])
def customer_login():
    """Customer login endpoint for portal access"""
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    customer = Customer.query.filter_by(email=data['email']).first()

    if not customer or not customer.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    # Update last login
    customer.last_login = datetime.utcnow()
    db.session.commit()

    # Create JWT token with customer ID and a 'customer' identifier
    access_token = create_access_token(
        identity=str(customer.id),
        additional_claims={'type': 'customer'}
    )

    return jsonify({
        'access_token': access_token,
        'customer': customer.to_dict()
    }), 200


@customer_portal_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_customer():
    """Get current customer info"""
    customer_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify(customer.to_dict()), 200


@customer_portal_bp.route('/calls', methods=['GET'])
@jwt_required()
def get_customer_calls():
    """Get all calls for the current customer"""
    customer_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Get query parameters for filtering
    status = request.args.get('status')  # 'handled', 'unhandled', 'all'
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    # Build query - exclude archived by default
    query = Call.query.filter_by(customer_id=customer_id, archived=False)

    # Filter by status if provided
    if status == 'handled':
        query = query.filter_by(handled=True)
    elif status == 'unhandled':
        query = query.filter_by(handled=False)

    # Order by most recent first
    query = query.order_by(Call.created_at.desc())

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    calls = query.limit(limit).offset(offset).all()

    return jsonify({
        'calls': [call.to_dict() for call in calls],
        'total': total_count,
        'limit': limit,
        'offset': offset
    }), 200


@customer_portal_bp.route('/calls/<int:call_id>', methods=['GET'])
@jwt_required()
def get_call_detail(call_id):
    """Get detailed information about a specific call"""
    customer_id = int(get_jwt_identity())

    # Verify this call belongs to this customer
    call = Call.query.filter_by(id=call_id, customer_id=customer_id).first()

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    # Get full transcript
    transcript = CallLog.query.filter_by(call_id=call.id).order_by(CallLog.created_at).all()

    call_data = call.to_dict()
    call_data['transcript'] = [
        {
            'speaker': log.speaker,
            'message': log.message,
            'timestamp': log.created_at.isoformat() if log.created_at else None
        }
        for log in transcript
    ]

    return jsonify(call_data), 200


@customer_portal_bp.route('/calls/<int:call_id>/mark-handled', methods=['POST'])
@jwt_required()
def mark_call_handled(call_id):
    """Mark a call as handled"""
    customer_id = int(get_jwt_identity())

    # Verify this call belongs to this customer
    call = Call.query.filter_by(id=call_id, customer_id=customer_id).first()

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    call.handled = True
    call.handled_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Call marked as handled',
        'call': call.to_dict()
    }), 200


@customer_portal_bp.route('/calls/<int:call_id>/mark-unhandled', methods=['POST'])
@jwt_required()
def mark_call_unhandled(call_id):
    """Mark a call as unhandled"""
    customer_id = int(get_jwt_identity())

    # Verify this call belongs to this customer
    call = Call.query.filter_by(id=call_id, customer_id=customer_id).first()

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    call.handled = False
    call.handled_at = None
    db.session.commit()

    return jsonify({
        'message': 'Call marked as unhandled',
        'call': call.to_dict()
    }), 200


@customer_portal_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_customer_settings():
    """Update customer settings (business info, AI config, etc.)"""
    customer_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    # Update allowed fields
    if 'business_name' in data:
        customer.business_name = data['business_name']
    if 'contact_name' in data:
        customer.contact_name = data['contact_name']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'business_type' in data:
        customer.business_type = data['business_type']
    if 'business_hours' in data:
        customer.business_hours = data['business_hours']
    if 'greeting_message' in data:
        customer.greeting_message = data['greeting_message']
    if 'ai_instructions' in data:
        customer.ai_instructions = data['ai_instructions']
    if 'notification_email' in data:
        customer.notification_email = data['notification_email']
    if 'notification_phone' in data:
        customer.notification_phone = data['notification_phone']

    db.session.commit()

    return jsonify({
        'message': 'Settings updated successfully',
        'customer': customer.to_dict()
    }), 200


@customer_portal_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_customer_password():
    """Change customer password"""
    customer_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password required'}), 400

    # Verify current password
    if not customer.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401

    # Set new password
    customer.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200


@customer_portal_bp.route('/calls/bulk-archive', methods=['POST'])
@jwt_required()
def bulk_archive_calls():
    """Archive multiple calls"""
    customer_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or not data.get('call_ids'):
        return jsonify({'error': 'call_ids required'}), 400

    call_ids = data['call_ids']

    # Verify all calls belong to this customer and archive them
    calls = Call.query.filter(
        Call.id.in_(call_ids),
        Call.customer_id == customer_id
    ).all()

    if len(calls) != len(call_ids):
        return jsonify({'error': 'Some calls not found or do not belong to you'}), 404

    for call in calls:
        call.archived = True
        call.archived_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        'message': f'{len(calls)} call(s) archived successfully',
        'archived_count': len(calls)
    }), 200


@customer_portal_bp.route('/calls/<int:call_id>/archive', methods=['POST'])
@jwt_required()
def archive_call(call_id):
    """Archive a single call"""
    customer_id = int(get_jwt_identity())

    call = Call.query.filter_by(id=call_id, customer_id=customer_id).first()

    if not call:
        return jsonify({'error': 'Call not found'}), 404

    call.archived = True
    call.archived_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Call archived successfully',
        'call': call.to_dict()
    }), 200


@customer_portal_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_customer_stats():
    """Get statistics for current customer"""
    customer_id = int(get_jwt_identity())
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    from sqlalchemy import func

    # Only count non-archived calls
    total_calls = Call.query.filter_by(customer_id=customer_id, archived=False).count()
    handled_calls = Call.query.filter_by(customer_id=customer_id, handled=True, archived=False).count()
    unhandled_calls = Call.query.filter_by(customer_id=customer_id, handled=False, archived=False).count()

    # Calls today (non-archived)
    calls_today = Call.query.filter_by(customer_id=customer_id, archived=False).filter(
        func.date(Call.created_at) == func.current_date()
    ).count()

    # Average call duration (non-archived)
    avg_duration = db.session.query(func.avg(Call.duration_seconds)).filter(
        Call.customer_id == customer_id,
        Call.archived == False
    ).scalar() or 0

    return jsonify({
        'total_calls': total_calls,
        'handled_calls': handled_calls,
        'unhandled_calls': unhandled_calls,
        'calls_today': calls_today,
        'avg_duration_seconds': round(avg_duration, 2),
        'subscription_status': customer.subscription_status,
        'subscription_tier': customer.subscription_tier
    }), 200
