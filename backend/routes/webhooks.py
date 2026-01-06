from flask import Blueprint, request, jsonify, current_app, send_file
from models import db, Customer, Call, CallLog
from datetime import datetime
from io import BytesIO
from urllib.parse import quote
import html
import os
from twilio.request_validator import RequestValidator

webhooks_bp = Blueprint('webhooks', __name__)

def validate_twilio_request():
    """Validate that the request is actually from Twilio"""
    validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))

    # Get the URL that Twilio called (from X-Forwarded-Proto if behind proxy)
    url = request.url
    if request.headers.get('X-Forwarded-Proto'):
        url = url.replace('http://', 'https://')

    # Get the signature from the request headers
    signature = request.headers.get('X-Twilio-Signature', '')

    # Validate the request
    return validator.validate(url, request.form, signature)

@webhooks_bp.route('/twilio/voice', methods=['POST'])
def twilio_voice_webhook():
    """
    Webhook endpoint for Twilio incoming calls
    This will be called when a call comes in to a DeskRinger number
    """
    # Validate request is from Twilio
    if not validate_twilio_request():
        return jsonify({'error': 'Invalid request signature'}), 403

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

    # Return TwiML response to start AI conversation with OpenAI
    greeting = customer.greeting_message or f"Thank you for calling {customer.business_name}. How can I help you today?"

    api_base_url = current_app.config['API_BASE_URL']
    gather_url = f"{api_base_url}/api/webhooks/twilio/gather"

    # Use OpenAI TTS voice via <Play> for the greeting (URL encode the text)
    greeting_audio_url = f"{api_base_url}/api/webhooks/twilio/tts?text={quote(greeting)}&amp;call_id={call.id}"

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Play>{greeting_audio_url}</Play>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="2.0" profanityFilter="false">
        </Gather>
        <Say>Sorry, I didn't catch that. Are you still there?</Say>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="2.0" profanityFilter="false">
        </Gather>
        <Say>I'm having trouble hearing you. Feel free to call back anytime!</Say>
        <Hangup/>
    </Response>'''

    return twiml, 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/gather', methods=['POST'])
def twilio_gather_webhook():
    """
    Webhook for processing speech input from caller
    Uses OpenAI GPT-4 for intelligent responses and TTS for natural voice
    """
    # Validate request is from Twilio
    if not validate_twilio_request():
        return jsonify({'error': 'Invalid request signature'}), 403

    from services.ai_service import AIService

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

    # Get conversation history from previous call logs
    previous_logs = CallLog.query.filter_by(call_id=call.id).order_by(CallLog.created_at).all()
    conversation_history = []
    for prev_log in previous_logs[:-1]:  # Exclude the current message we just added
        role = "user" if prev_log.speaker == "caller" else "assistant"
        conversation_history.append({"role": role, "content": prev_log.message})

    # Get AI response using GPT-4
    ai_service = AIService()
    ai_response = ai_service.get_response(call.customer, caller_message, conversation_history)

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

    # Use OpenAI TTS for natural-sounding response
    api_base_url = current_app.config['API_BASE_URL']
    audio_url = f"{api_base_url}/api/webhooks/twilio/tts?text={quote(ai_response)}&amp;call_id={call.id}"
    gather_url = f"{api_base_url}/api/webhooks/twilio/gather"

    # Continue conversation or end call based on context
    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Play>{audio_url}</Play>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="2.0" profanityFilter="false">
        </Gather>
        <Play>{api_base_url}/api/webhooks/twilio/tts?text={quote("Are you still there? Anything else I can help with?")}&amp;call_id={call.id}</Play>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="2.0" profanityFilter="false">
        </Gather>
        <Play>{api_base_url}/api/webhooks/twilio/tts?text={quote("Okay, thanks for calling! Have a great day!")}&amp;call_id={call.id}</Play>
        <Hangup/>
    </Response>'''

    return twiml, 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/tts', methods=['GET'])
def twilio_tts_endpoint():
    """
    Generate speech audio using OpenAI TTS
    Twilio will request this URL to get the audio
    """
    from services.ai_service import AIService

    text = request.args.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Generate speech using OpenAI TTS
        ai_service = AIService()
        audio_data = ai_service.text_to_speech(text)

        # Return as audio file
        return send_file(
            BytesIO(audio_data),
            mimetype='audio/mpeg',
            as_attachment=False
        )

    except Exception as e:
        print(f"TTS Error: {e}")
        # Fallback to empty audio or error
        return jsonify({'error': str(e)}), 500


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

        # Send notifications if call completed successfully
        if call_status == 'completed' and call.customer:
            try:
                from services.notification_service import NotificationService
                notification_service = NotificationService()

                # Generate summary of the call
                summary = notification_service.generate_summary(call.customer, call)

                # Save summary to call record for customer portal
                call.summary = summary
                db.session.commit()

                # Send email and/or SMS notification
                notification_service.send_call_notification(call.customer, call, summary)

                print(f"Notifications sent for call {call.id}")
            except Exception as e:
                print(f"Error sending notifications for call {call.id}: {e}")

    return jsonify({'status': 'ok'}), 200


@webhooks_bp.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Webhook for Stripe payment events
    Handle subscription created, updated, cancelled, payment failed, etc.
    """
    import stripe
    import os

    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        print(f"Invalid payload: {e}")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print(f"Invalid signature: {e}")
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle different event types
    event_type = event['type']
    data = event['data']['object']

    print(f"Stripe webhook received: {event_type}")

    # Handle subscription events
    if event_type == 'customer.subscription.created':
        # New subscription created
        stripe_customer_id = data['customer']
        stripe_subscription_id = data['id']
        status = data['status']  # active, trialing, etc.

        # Find customer by Stripe customer ID
        customer = Customer.query.filter_by(stripe_customer_id=stripe_customer_id).first()

        if customer:
            customer.stripe_subscription_id = stripe_subscription_id
            customer.subscription_status = 'active' if status == 'active' else status
            db.session.commit()
            print(f"Subscription created for customer {customer.id}")

    elif event_type == 'customer.subscription.updated':
        # Subscription updated (plan change, status change, etc.)
        stripe_subscription_id = data['id']
        status = data['status']

        customer = Customer.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()

        if customer:
            customer.subscription_status = 'active' if status == 'active' else status
            db.session.commit()
            print(f"Subscription updated for customer {customer.id}: {status}")

    elif event_type == 'customer.subscription.deleted':
        # Subscription cancelled
        stripe_subscription_id = data['id']

        customer = Customer.query.filter_by(stripe_subscription_id=stripe_subscription_id).first()

        if customer:
            customer.subscription_status = 'cancelled'
            customer.cancelled_at = datetime.utcnow()
            db.session.commit()
            print(f"Subscription cancelled for customer {customer.id}")

    elif event_type == 'invoice.payment_succeeded':
        # Payment succeeded
        stripe_customer_id = data['customer']

        customer = Customer.query.filter_by(stripe_customer_id=stripe_customer_id).first()

        if customer and customer.subscription_status != 'active':
            customer.subscription_status = 'active'
            db.session.commit()
            print(f"Payment succeeded for customer {customer.id}")

    elif event_type == 'invoice.payment_failed':
        # Payment failed
        stripe_customer_id = data['customer']

        customer = Customer.query.filter_by(stripe_customer_id=stripe_customer_id).first()

        if customer:
            customer.subscription_status = 'past_due'
            db.session.commit()
            print(f"Payment failed for customer {customer.id}")

    return jsonify({'status': 'success'}), 200
