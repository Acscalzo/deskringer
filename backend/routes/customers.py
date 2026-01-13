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
    """Create a new customer with auto-generated password and welcome email"""
    import secrets
    import string
    data = request.get_json()

    if not data or not data.get('business_name') or not data.get('email'):
        return jsonify({'error': 'Business name and email required'}), 400

    # Check if email already exists
    if Customer.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    # Generate temporary password (12 characters, mix of letters and numbers)
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

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
        greeting_message=data.get('greeting_message', f'Thank you for calling {data["business_name"]}. How can I help you today?'),
        ai_instructions=data.get('ai_instructions'),
        notification_email=data['email'],  # Default notification email to their login email
        subscription_status='trial',
        trial_ends_at=datetime.utcnow() + timedelta(days=7)
    )

    # Set the temporary password
    customer.set_password(temp_password)

    db.session.add(customer)
    db.session.commit()

    # Send welcome email with credentials
    send_welcome = data.get('send_welcome_email', True)  # Default to True
    if send_welcome:
        try:
            send_welcome_email(customer, temp_password)
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            # Don't fail customer creation if email fails

    return jsonify({
        'message': 'Customer created successfully',
        'customer': customer.to_dict(),
        'temporary_password': temp_password  # Return it so admin can see it
    }), 201


def send_welcome_email(customer, temp_password):
    """Send welcome email to new customer with login credentials"""
    import os
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, From

    if not os.environ.get('SENDGRID_API_KEY'):
        print("SendGrid not configured, skipping welcome email")
        return

    from_email = os.environ.get('NOTIFICATION_FROM_EMAIL', 'notifications@deskringer.com')
    from_name = os.environ.get('NOTIFICATION_FROM_NAME', 'DeskRinger')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #6366f1; color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }}
            .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
            .credentials {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #6366f1; }}
            .btn {{ background: #6366f1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 20px 0; font-weight: 600; }}
            .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin: 0; font-size: 28px;">Welcome to DeskRinger!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Your AI receptionist is ready</p>
            </div>

            <div class="content">
                <h2 style="color: #111827; margin-top: 0;">Hello{" " + customer.contact_name if customer.contact_name else ""}!</h2>

                <p style="color: #374151; line-height: 1.6;">
                    Thank you for choosing DeskRinger. Your AI-powered receptionist service is now active and ready to answer calls for <strong>{customer.business_name}</strong>.
                </p>

                <div class="credentials">
                    <h3 style="margin-top: 0; color: #111827;">Your Login Credentials</h3>
                    <p style="margin: 10px 0;"><strong>Email:</strong> {customer.email}</p>
                    <p style="margin: 10px 0;"><strong>Temporary Password:</strong> <code style="background: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-family: monospace;">{temp_password}</code></p>
                    <p style="color: #ef4444; font-size: 14px; margin-top: 15px;">
                        <strong>Important:</strong> Please change your password after logging in for the first time.
                    </p>
                </div>

                <div style="text-align: center;">
                    <a href="https://portal.deskringer.com" class="btn">
                        Access Your Dashboard
                    </a>
                </div>

                <h3 style="color: #111827; margin-top: 30px;">What's Next?</h3>
                <ol style="color: #374151; line-height: 1.8;">
                    <li>Log in to your customer portal</li>
                    <li>Configure your business settings and AI instructions</li>
                    <li>Set up call forwarding if needed</li>
                    <li>Test your DeskRinger number{": " + customer.deskringer_number if customer.deskringer_number else ""}</li>
                    <li>Start receiving calls!</li>
                </ol>

                <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                    <strong style="color: #1e40af;">Your Trial Period:</strong>
                    <p style="margin: 8px 0 0 0; color: #1e3a8a;">
                        You have a 7-day trial to test DeskRinger risk-free. We'll follow up before your trial ends.
                    </p>
                </div>

                <p style="color: #374151; line-height: 1.6; margin-top: 30px;">
                    If you have any questions or need help getting started, please don't hesitate to reach out.
                </p>
            </div>

            <div class="footer">
                <p>DeskRinger - AI Receptionist Service</p>
                <p>This is an automated message. Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = Mail(
        from_email=From(from_email, from_name),
        to_emails=customer.email,
        subject=f'Welcome to DeskRinger - Your Account is Ready!',
        html_content=html_content
    )

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(f"Welcome email sent to {customer.email}: {response.status_code}")


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


@customers_bp.route('/<int:customer_id>/set-password', methods=['POST'])
@jwt_required()
def set_customer_password(customer_id):
    """Set password for customer portal access (admin only)"""
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    data = request.get_json()

    if not data or not data.get('password'):
        return jsonify({'error': 'Password required'}), 400

    # Validate password length
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    # Set password for customer portal access
    customer.set_password(data['password'])
    db.session.commit()

    return jsonify({
        'message': 'Password set successfully',
        'customer': {
            'id': customer.id,
            'email': customer.email,
            'business_name': customer.business_name,
            'has_portal_access': True
        }
    }), 200
