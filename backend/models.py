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
    business_hours = db.Column(db.JSON)  # Store hours as JSON: {monday: {open: "9:00", close: "17:00"}, ...}
    holiday_hours = db.Column(db.Text)  # Special holiday hours information

    # DeskRinger phone number assigned to this customer
    deskringer_number = db.Column(db.String(20), unique=True, index=True)

    # Forwarding settings
    forward_to_number = db.Column(db.String(20))  # Customer's actual business phone

    # AI Configuration - Structured fields for easier customization
    greeting_message = db.Column(db.Text)  # Custom greeting
    services_offered = db.Column(db.Text)  # What services does the business provide?
    faqs = db.Column(db.JSON)  # List of {question, answer} pairs
    appointment_handling = db.Column(db.String(50), default='collect_details')  # collect_details, callback, transfer, booking_link, call_back_later
    pricing_info = db.Column(db.Text)  # Pricing information to share
    special_instructions = db.Column(db.Text)  # Any other specific instructions

    # Compiled AI instructions (generated from above fields)
    ai_instructions = db.Column(db.Text)  # Full compiled instructions for AI behavior

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

    def compile_ai_instructions(self):
        """Compile structured fields into final AI instructions"""
        instructions = []

        # Business context
        if self.business_type:
            instructions.append(f"Business Type: {self.business_type}")

        if self.business_name:
            instructions.append(f"Business Name: {self.business_name}")

        # Services offered
        if self.services_offered:
            instructions.append(f"\nServices Offered:\n{self.services_offered}")

        # Business hours
        if self.business_hours:
            hours_text = "\nBusiness Hours:"
            days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days_order:
                if day in self.business_hours:
                    day_info = self.business_hours[day]
                    if day_info.get('closed'):
                        hours_text += f"\n{day.capitalize()}: Closed"
                    elif day_info.get('open') and day_info.get('close'):
                        hours_text += f"\n{day.capitalize()}: {day_info['open']} - {day_info['close']}"
            instructions.append(hours_text)

        # Holiday hours
        if self.holiday_hours:
            instructions.append(f"\nHoliday Hours:\n{self.holiday_hours}")

        # FAQs
        if self.faqs and len(self.faqs) > 0:
            instructions.append("\nFrequently Asked Questions:")
            for faq in self.faqs:
                q = faq.get('question', '')
                a = faq.get('answer', '')
                if q and a:
                    instructions.append(f"Q: {q}\nA: {a}")

        # Appointment/ticket handling
        if self.appointment_handling == 'collect_details':
            instructions.append("""
Appointment/Request Handling:
Collect the following information from the caller:
- Full name
- Phone number for callback
- Requested appointment date/time (if scheduling an appointment)
- Delivery address (if requesting delivery)
- Brief description of what they need
- Any special requests or notes

After collecting information, confirm the details with the caller and let them know someone will contact them shortly to confirm.""")
        elif self.appointment_handling == 'callback':
            instructions.append("""
Appointment/Request Handling:
Take the caller's name and phone number, then let them know someone will call them back shortly to help with their request.""")
        elif self.appointment_handling == 'transfer':
            instructions.append("""
Appointment/Request Handling:
Inform the caller you'll transfer them to a staff member who can help them immediately.""")
        elif self.appointment_handling == 'booking_link':
            instructions.append("""
Appointment/Request Handling:
Provide the caller with our online booking information or website where they can schedule an appointment.""")
        elif self.appointment_handling == 'call_back_later':
            instructions.append("""
Appointment/Request Handling:
Inform the caller of our business hours and ask them to call back during those times to speak with a staff member.""")

        # Pricing
        if self.pricing_info:
            instructions.append(f"\nPricing Information:\n{self.pricing_info}")

        # Special instructions
        if self.special_instructions:
            instructions.append(f"\nSpecial Instructions:\n{self.special_instructions}")

        # Transfer/Forward number
        if self.forward_to_number:
            instructions.append(f"""
Call Transfer:
If a caller asks to speak with someone directly, or if you cannot answer their question, you can transfer them to: {self.forward_to_number}
Always ask the caller if they would like to be transferred before doing so.""")

        # General behavior
        instructions.append("""
General Behavior:
- Be professional, friendly, and helpful
- Speak clearly and naturally
- If you don't know an answer, offer to transfer them to a staff member or have someone call them back
- Always thank the caller for calling""")

        return "\n".join(instructions)

    def to_dict(self, include_calls=False):
        data = {
            'id': self.id,
            'business_name': self.business_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'business_type': self.business_type,
            'business_hours': self.business_hours,
            'holiday_hours': self.holiday_hours,
            'deskringer_number': self.deskringer_number,
            'forward_to_number': self.forward_to_number,
            'greeting_message': self.greeting_message,
            'services_offered': self.services_offered,
            'faqs': self.faqs or [],
            'appointment_handling': self.appointment_handling,
            'pricing_info': self.pricing_info,
            'special_instructions': self.special_instructions,
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
    archived = db.Column(db.Boolean, default=False)  # Has customer archived this call?
    archived_at = db.Column(db.DateTime)  # When was it archived?

    # Costs (for tracking)
    twilio_cost = db.Column(db.Float)
    openai_cost = db.Column(db.Float)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ended_at = db.Column(db.DateTime)

    # Relationships
    logs = db.relationship('CallLog', backref='call', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_logs=False, admin_view=False):
        """
        Convert call to dictionary

        Args:
            include_logs: Include detailed call logs
            admin_view: For admin dashboard - includes customer name but NOT transcript
        """
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'caller_phone': self.caller_phone,
            'caller_name': self.caller_name,
            'twilio_call_sid': self.twilio_call_sid,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'intent': self.intent,
            'callback_requested': self.callback_requested,
            'handled': self.handled,
            'handled_at': self.handled_at.isoformat() if self.handled_at else None,
            'archived': self.archived,
            'archived_at': self.archived_at.isoformat() if self.archived_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None
        }

        # Include customer business name for admin view
        if admin_view and self.customer:
            data['customer_business_name'] = self.customer.business_name
            # Admin can see summary but NOT full transcript (Option B privacy)
            data['summary'] = self.summary
        else:
            # Customer portal view - include full transcript
            data['transcript'] = self.transcript
            data['summary'] = self.summary

        if include_logs:
            # Only include logs for customer view, not admin
            if not admin_view:
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
