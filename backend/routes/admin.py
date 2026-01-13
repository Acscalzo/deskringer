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

    # Create JWT token (convert ID to string for Flask-JWT-Extended)
    access_token = create_access_token(identity=str(admin.id))

    return jsonify({
        'access_token': access_token,
        'admin': admin.to_dict()
    }), 200


@admin_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_admin():
    """Get current admin user info"""
    admin_id = int(get_jwt_identity())  # Convert back to int for database query
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    return jsonify(admin.to_dict()), 200


@admin_bp.route('/create', methods=['POST'])
@jwt_required()
def create_admin():
    """Create a new admin user (requires authentication)"""
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


@admin_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change admin password"""
    admin_id = int(get_jwt_identity())
    admin = Admin.query.get(admin_id)

    if not admin:
        return jsonify({'error': 'Admin not found'}), 404

    data = request.get_json()

    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current password and new password required'}), 400

    # Verify current password
    if not admin.check_password(data['current_password']):
        return jsonify({'error': 'Current password is incorrect'}), 401

    # Set new password
    admin.set_password(data['new_password'])
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get dashboard statistics"""
    # Verify admin is authenticated (identity will be string from JWT)
    admin_id = int(get_jwt_identity())
    from models import Customer, Call
    from sqlalchemy import func

    total_customers = Customer.query.count()
    active_customers = Customer.query.filter_by(subscription_status='active').count()
    trial_customers = Customer.query.filter_by(subscription_status='trial').count()

    total_calls = Call.query.count()

    from datetime import date
    today = date.today()
    calls_today = Call.query.filter(
        func.date(Call.created_at) == today
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


@admin_bp.route('/trial-customers', methods=['GET'])
@jwt_required()
def get_trial_customers():
    """Get all customers on trial with expiration info"""
    from models import Customer
    from datetime import datetime, timedelta

    # Get all trial customers
    trial_customers = Customer.query.filter_by(subscription_status='trial').order_by(Customer.trial_ends_at).all()

    customers_data = []
    for customer in trial_customers:
        # Calculate days remaining
        days_remaining = None
        is_expired = False
        if customer.trial_ends_at:
            delta = customer.trial_ends_at - datetime.utcnow()
            days_remaining = delta.days
            is_expired = days_remaining < 0

        customers_data.append({
            'id': customer.id,
            'business_name': customer.business_name,
            'contact_name': customer.contact_name,
            'email': customer.email,
            'created_at': customer.created_at.isoformat() if customer.created_at else None,
            'trial_ends_at': customer.trial_ends_at.isoformat() if customer.trial_ends_at else None,
            'days_remaining': days_remaining,
            'is_expired': is_expired,
            'last_login': customer.last_login.isoformat() if customer.last_login else None
        })

    return jsonify({
        'trial_customers': customers_data,
        'count': len(customers_data)
    }), 200


@admin_bp.route('/test-email', methods=['POST'])
@jwt_required()
def test_email():
    """Test email notification configuration"""
    data = request.get_json()

    if not data or not data.get('email'):
        return jsonify({'error': 'Email address required'}), 400

    test_email = data['email']

    try:
        from services.notification_service import NotificationService
        import os

        # Check if SendGrid is configured
        if not os.environ.get('SENDGRID_API_KEY'):
            return jsonify({
                'error': 'SendGrid not configured',
                'details': 'SENDGRID_API_KEY environment variable is not set'
            }), 400

        # Create a test notification
        notification_service = NotificationService()

        # Build test email
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=notification_service.from_email,
            to_emails=test_email,
            subject='DeskRinger Email Test',
            html_content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #6366f1; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                    .content {{ background: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; margin-top: 20px; border-radius: 8px; }}
                    .success {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 15px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">DeskRinger Email Test</h1>
                    </div>
                    <div class="content">
                        <div class="success">
                            <strong style="color: #065f46;">Success!</strong>
                            <p style="margin: 8px 0 0 0; color: #047857;">Your email notifications are configured correctly and working.</p>
                        </div>
                        <p>This is a test email sent from your DeskRinger admin dashboard.</p>
                        <p>When calls are completed, your customers will receive notifications similar to this one with:</p>
                        <ul>
                            <li>Caller information</li>
                            <li>AI-generated call summary</li>
                            <li>Full transcript</li>
                            <li>Link to dashboard</li>
                        </ul>
                        <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )

        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)

        return jsonify({
            'success': True,
            'message': f'Test email sent successfully to {test_email}',
            'status_code': response.status_code
        }), 200

    except Exception as e:
        print(f"Error sending test email: {e}")
        return jsonify({
            'error': 'Failed to send test email',
            'details': str(e)
        }), 500
