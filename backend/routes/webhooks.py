from flask import Blueprint, request, jsonify, current_app
from models import db, Customer, Call, CallLog
from datetime import datetime
import html

webhooks_bp = Blueprint('webhooks', __name__)

@webhooks_bp.route('/twilio/voice', methods=['POST'])
def twilio_voice_webhook():
    """
    Webhook endpoint for Twilio incoming calls
    This will be called when a call comes in to a DeskRinger number
    """
    # Get Twilio request data
    from_number = request.values.get('From')
    to_number = request.values.get('To')
    call_sid = request.values.get('CallSid')
    call_status = request.values.get('CallStatus')

    # Find customer by their DeskRinger number
    customer = Customer.query.filter_by(deskringer_number=to_number).first()

    if not customer:
        # No customer found for this number
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>This number is not currently active. Please contact support.</Say>
            <Hangup/>
        </Response>''', 200, {'Content-Type': 'text/xml'}

    # Create call record
    call = Call(
        customer_id=customer.id,
        caller_phone=from_number,
        twilio_call_sid=call_sid,
        status='in_progress'
    )
    db.session.add(call)
    db.session.commit()

    # Return TwiML response to start AI conversation
    # This is a placeholder - you'll integrate OpenAI Realtime API here
    greeting = customer.greeting_message or f"Thank you for calling {customer.business_name}. How can I help you today?"

    # Escape XML special characters in greeting
    greeting_escaped = html.escape(greeting)

    # Use absolute URL for Gather action
    api_base_url = current_app.config['API_BASE_URL']
    gather_url = f"{api_base_url}/api/webhooks/twilio/gather"

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="Polly.Joanna">{greeting_escaped}</Say>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="auto">
            <Say>Please tell me how I can help you.</Say>
        </Gather>
        <Say>I didn't hear anything. Goodbye.</Say>
        <Hangup/>
    </Response>'''

    return twiml, 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/gather', methods=['POST'])
def twilio_gather_webhook():
    """
    Webhook for processing speech input from caller
    This is where you'll integrate OpenAI for AI responses
    """
    speech_result = request.values.get('SpeechResult')
    call_sid = request.values.get('CallSid')

    # Find the call
    call = Call.query.filter_by(twilio_call_sid=call_sid).first()

    if not call:
        return '''<?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>I'm sorry, there was an error. Goodbye.</Say>
            <Hangup/>
        </Response>''', 200, {'Content-Type': 'text/xml'}

    # Log the caller's speech
    caller_message = speech_result or '[No speech detected]'
    log = CallLog(
        call_id=call.id,
        speaker='caller',
        message=caller_message
    )
    db.session.add(log)

    # TODO: Process with OpenAI and generate response
    # For now, just acknowledge
    ai_response = "Thank you for your message. Someone will get back to you shortly."

    # Log AI response
    log = CallLog(
        call_id=call.id,
        speaker='ai',
        message=ai_response
    )
    db.session.add(log)

    # Update the Call transcript with the full conversation
    if call.transcript:
        call.transcript += f"\n\nCaller: {caller_message}\nAI: {ai_response}"
    else:
        call.transcript = f"Caller: {caller_message}\nAI: {ai_response}"

    db.session.commit()

    # Escape XML special characters in AI response
    ai_response_escaped = html.escape(ai_response)

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="Polly.Joanna">{ai_response_escaped}</Say>
        <Say>Goodbye!</Say>
        <Hangup/>
    </Response>'''

    return twiml, 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/status', methods=['POST'])
def twilio_status_webhook():
    """
    Webhook for call status updates (completed, failed, etc.)
    """
    call_sid = request.values.get('CallSid')
    call_status = request.values.get('CallStatus')
    call_duration = request.values.get('CallDuration', type=int)
    recording_url = request.values.get('RecordingUrl')

    # Find the call
    call = Call.query.filter_by(twilio_call_sid=call_sid).first()

    if call:
        call.status = call_status
        call.duration_seconds = call_duration
        call.twilio_recording_url = recording_url
        call.ended_at = datetime.utcnow()

        # Calculate Twilio cost (approximate: $0.0085/min for voice)
        if call_duration:
            call.twilio_cost = (call_duration / 60) * 0.0085

        db.session.commit()

    return jsonify({'status': 'ok'}), 200


@webhooks_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook for Stripe payment events
    Handle subscription created, updated, cancelled, payment failed, etc.
    """
    # TODO: Implement Stripe webhook handling
    # Verify webhook signature
    # Process events: customer.subscription.created, updated, deleted, etc.
    # Update customer subscription status in database

    return jsonify({'status': 'ok'}), 200
