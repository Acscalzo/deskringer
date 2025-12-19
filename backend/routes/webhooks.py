from flask import Blueprint, request, jsonify, current_app, send_file
from models import db, Customer, Call, CallLog
from datetime import datetime
from io import BytesIO
from urllib.parse import quote
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

    # Return TwiML response to start AI conversation with OpenAI
    greeting = customer.greeting_message or f"Thank you for calling {customer.business_name}. How can I help you today?"

    api_base_url = current_app.config['API_BASE_URL']
    gather_url = f"{api_base_url}/api/webhooks/twilio/gather"

    # Use OpenAI TTS voice via <Play> for the greeting (URL encode the text)
    greeting_audio_url = f"{api_base_url}/api/webhooks/twilio/tts?text={quote(greeting)}&amp;call_id={call.id}"

    twiml = f'''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Play>{greeting_audio_url}</Play>
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="auto">
            <Pause length="1"/>
        </Gather>
        <Say>I didn't hear anything. Goodbye.</Say>
        <Hangup/>
    </Response>'''

    return twiml, 200, {'Content-Type': 'text/xml'}


@webhooks_bp.route('/twilio/gather', methods=['POST'])
def twilio_gather_webhook():
    """
    Webhook for processing speech input from caller
    Uses OpenAI GPT-4 for intelligent responses and TTS for natural voice
    """
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
        <Gather input="speech" action="{gather_url}" method="POST" timeout="5" speechTimeout="auto">
            <Pause length="1"/>
        </Gather>
        <Play>{api_base_url}/api/webhooks/twilio/tts?text={quote("Goodbye!")}&amp;call_id={call.id}</Play>
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
