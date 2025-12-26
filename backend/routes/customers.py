from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Customer
from datetime import datetime, timedelta

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/', methods=['GET'])
@jwt_required()
def get_customers():
    """Get all customers with optional filtering"""
    status = request.args.get('status')  # active, trial, cancelled, etc.
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Customer.query

    if status:
        query = query.filter_by(subscription_status=status)

    # Order by most recent first
    query = query.order_by(Customer.created_at.desc())

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'customers': [customer.to_dict() for customer in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
        'per_page': per_page
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    """Get a specific customer with details"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    return jsonify(customer.to_dict(include_calls=True)), 200


@customers_bp.route('/', methods=['POST'])
@jwt_required()
def create_customer():
    """Create a new customer"""
    data = request.get_json()

    if not data or not data.get('business_name') or not data.get('email'):
        return jsonify({'error': 'Business name and email required'}), 400

    # Check if email already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Create customer with trial period (7 days)
    customer = Customer(
        business_name=data['business_name'],
        contact_name=data.get('contact_name'),
        email=data['email'],
        phone=data.get('phone'),
        deskringer_number=data.get('deskringer_number'),
        business_type=data.get('business_type'),
        business_hours=data.get('business_hours'),
        forward_to_number=data.get('forward_to_number'),
        greeting_message=data.get('greeting_message', 'Thank you for calling {business_name}. How can I help you today?'),
        ai_instructions=data.get('ai_instructions'),
        subscription_status='trial',
        trial_ends_at=datetime.utcnow() + timedelta(days=7)
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify({
        'message': 'Customer created successfully',
        'customer': customer.to_dict()
    }), 201


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    """Update customer details"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    # Update allowed fields
    allowed_fields = [
        'business_name', 'contact_name', 'email', 'phone', 'deskringer_number',
        'business_type', 'business_hours', 'forward_to_number',
        'greeting_message', 'ai_instructions', 'subscription_status',
        'subscription_tier', 'notification_email', 'notification_phone',
        'notification_instructions'
    ]

    for field in allowed_fields:
        if field in data:
            setattr(customer, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Customer updated successfully',
        'customer': customer.to_dict()
    }), 200


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    """Delete a customer (soft delete by marking as cancelled)"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    customer.subscription_status = 'cancelled'
    customer.cancelled_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': 'Customer cancelled successfully'}), 200


@customers_bp.route('/<int:customer_id>/settings', methods=['PUT'])
@jwt_required()
def update_customer_settings(customer_id):
    """Update customer AI settings (greeting, instructions, etc.)"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    # Update AI-specific settings
    if 'greeting_message' in data:
        customer.greeting_message = data['greeting_message']

    if 'ai_instructions' in data:
        customer.ai_instructions = data['ai_instructions']

    if 'business_hours' in data:
        customer.business_hours = data['business_hours']

    db.session.commit()

    return jsonify({
        'message': 'Settings updated successfully',
        'customer': customer.to_dict()
    }), 200
