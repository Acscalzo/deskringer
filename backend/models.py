from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Admin(db.Model):
    """Admin users who can access the admin dashboard"""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class Customer(db.Model):
    """Businesses that subscribe to DeskRinger"""
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))  # Password for customer portal access
    phone = db.Column(db.String(20))
    last_login = db.Column(db.DateTime)  # Track when customer last logged into portal

    # Business details
    business_type = db.Column(db.String(50))  # salon, dental, gym, etc.
    business_hours = db.Column(db.JSON)  # Store hours as JSON

    # DeskRinger phone number assigned to this customer
    deskringer_number = db.Column(db.String(20), unique=True, index=True)

    # Forwarding settings
    forward_to_number = db.Column(db.String(20))  # Customer's actual business phone

    # AI Configuration
    greeting_message = db.Column(db.Text)  # Custom greeting
    ai_instructions = db.Column(db.Text)  # Custom instructions for AI behavior

    # Notification Settings
    notification_email = db.Column(db.String(120))  # Where to send call notifications (defaults to email)
    notification_phone = db.Column(db.String(20))  # Where to send SMS notifications
    notification_instructions = db.Column(db.Text)  # How to format notifications for this business

    # Subscription
    subscription_status = db.Column(db.String(20), default='trial')  # trial, active, cancelled, past_due
    subscription_tier = db.Column(db.String(20), default='basic')  # basic, premium
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    trial_ends_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    # Relationships
    calls = db.relationship('Call', backref='customer', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Set password hash for customer portal access"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check password for customer portal login"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_calls=False):
        data = {
            'id': self.id,
            'business_name': self.business_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'business_type': self.business_type,
            'business_hours': self.business_hours,
            'deskringer_number': self.deskringer_number,
            'forward_to_number': self.forward_to_number,
            'greeting_message': self.greeting_message,
            'ai_instructions': self.ai_instructions,
            'notification_email': self.notification_email,
            'notification_phone': self.notification_phone,
            'notification_instructions': self.notification_instructions,
            'subscription_status': self.subscription_status,
            'subscription_tier': self.subscription_tier,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'trial_ends_at': self.trial_ends_at.isoformat() if self.trial_ends_at else None
        }

        if include_calls:
            data['recent_calls'] = [call.to_dict() for call in self.calls.order_by(Call.created_at.desc()).limit(10)]

        return data


class Call(db.Model):
    """Individual calls received by the AI receptionist"""
    __tablename__ = 'calls'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)

    # Call details
    caller_phone = db.Column(db.String(20), nullable=False)
    caller_name = db.Column(db.String(100))  # If identified

    # Twilio data
    twilio_call_sid = db.Column(db.String(100), unique=True, index=True)
    twilio_recording_url = db.Column(db.String(500))

    # Call metadata
    duration_seconds = db.Column(db.Integer)
    status = db.Column(db.String(20))  # in_progress, completed, failed, no_answer
    direction = db.Column(db.String(20), default='inbound')  # inbound, outbound

    # AI interaction
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)  # AI-generated summary
    intent = db.Column(db.String(50))  # appointment, question, complaint, etc.
    callback_requested = db.Column(db.Boolean, default=False)

    # Customer portal tracking
    handled = db.Column(db.Boolean, default=False)  # Has customer marked this as handled?
    handled_at = db.Column(db.DateTime)  # When was it marked as handled?

    # Costs (for tracking)
    twilio_cost = db.Column(db.Float)
    openai_cost = db.Column(db.Float)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ended_at = db.Column(db.DateTime)

    # Relationships
    logs = db.relationship('CallLog', backref='call', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_logs=False):
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'caller_phone': self.caller_phone,
            'caller_name': self.caller_name,
            'twilio_call_sid': self.twilio_call_sid,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'transcript': self.transcript,
            'summary': self.summary,
            'intent': self.intent,
            'callback_requested': self.callback_requested,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None
        }

        if include_logs:
            data['logs'] = [log.to_dict() for log in self.logs.order_by(CallLog.created_at)]

        return data


class CallLog(db.Model):
    """Detailed logs of AI interactions during a call"""
    __tablename__ = 'call_logs'

    id = db.Column(db.Integer, primary_key=True)
    call_id = db.Column(db.Integer, db.ForeignKey('calls.id'), nullable=False, index=True)

    # Log entry
    speaker = db.Column(db.String(20))  # 'caller' or 'ai'
    message = db.Column(db.Text)

    # Metadata
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'call_id': self.call_id,
            'speaker': self.speaker,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
