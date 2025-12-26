"""
Notification Service for sending email and SMS alerts to business owners
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client


class NotificationService:
    """Handle sending notifications to business owners"""

    def __init__(self):
        # SendGrid for emails
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('NOTIFICATION_FROM_EMAIL', 'notifications@deskringer.com')

        # Twilio for SMS
        self.twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')

    def send_call_notification(self, customer, call, transcript_summary):
        """
        Send notification about a completed call

        Args:
            customer: Customer object
            call: Call object
            transcript_summary: AI-generated summary of the call
        """
        # Send email if configured
        if customer.notification_email and self.sendgrid_api_key:
            self._send_email_notification(customer, call, transcript_summary)

        # Send SMS if configured
        if customer.notification_phone and self.twilio_account_sid:
            self._send_sms_notification(customer, call, transcript_summary)

    def _send_email_notification(self, customer, call, transcript_summary):
        """Send email notification"""
        try:
            # Build email subject
            caller_id = call.caller_name or call.caller_phone
            subject = f"New call from {caller_id} - {customer.business_name}"

            # Build email body
            html_content = self._build_email_html(customer, call, transcript_summary)

            # Send email
            message = Mail(
                from_email=self.from_email,
                to_emails=customer.notification_email,
                subject=subject,
                html_content=html_content
            )

            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)

            print(f"Email notification sent to {customer.notification_email}: {response.status_code}")
            return True

        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False

    def _send_sms_notification(self, customer, call, transcript_summary):
        """Send SMS notification"""
        try:
            # Build SMS message (keep it short - 160 chars is ideal)
            caller_id = call.caller_name or call.caller_phone
            message_body = f"New call for {customer.business_name}\n"
            message_body += f"From: {caller_id}\n"
            message_body += f"Summary: {transcript_summary[:80]}...\n"
            message_body += f"View: https://admin.deskringer.com/calls"

            # Send SMS via Twilio
            client = Client(self.twilio_account_sid, self.twilio_auth_token)

            message = client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=customer.notification_phone
            )

            print(f"SMS notification sent to {customer.notification_phone}: {message.sid}")
            return True

        except Exception as e:
            print(f"Error sending SMS notification: {e}")
            return False

    def _build_email_html(self, customer, call, transcript_summary):
        """Build HTML email content"""

        caller_id = call.caller_name or call.caller_phone
        duration_mins = call.duration_seconds // 60 if call.duration_seconds else 0
        duration_secs = call.duration_seconds % 60 if call.duration_seconds else 0

        # Get custom formatting instructions if available
        custom_note = ""
        if customer.notification_instructions:
            custom_note = f"""
            <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0;">
                <strong>⚠️ Special Instructions:</strong>
                <p style="margin: 8px 0 0 0;">{customer.notification_instructions}</p>
            </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #6366f1; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .call-info {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3f4f6; }}
                .transcript {{ background: white; padding: 15px; border-radius: 6px; margin: 15px 0; max-height: 300px; overflow-y: auto; }}
                .btn {{ background: #6366f1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 10px 0; }}
                .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 24px;">📞 New Call Received</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{customer.business_name}</p>
                </div>

                <div class="content">
                    <div class="call-info">
                        <h2 style="margin-top: 0; color: #111827;">Call Summary</h2>
                        <div class="info-row">
                            <strong>Caller:</strong>
                            <span>{caller_id}</span>
                        </div>
                        <div class="info-row">
                            <strong>Phone:</strong>
                            <span><a href="tel:{call.caller_phone}">{call.caller_phone}</a></span>
                        </div>
                        <div class="info-row">
                            <strong>Duration:</strong>
                            <span>{duration_mins}m {duration_secs}s</span>
                        </div>
                        <div class="info-row">
                            <strong>Status:</strong>
                            <span style="color: #10b981;">✓ {call.status}</span>
                        </div>
                    </div>

                    {custom_note}

                    <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 15px 0;">
                        <strong style="color: #1e40af;">AI Summary:</strong>
                        <p style="margin: 8px 0 0 0; color: #1e3a8a;">{transcript_summary}</p>
                    </div>

                    <div class="transcript">
                        <h3 style="margin-top: 0; color: #111827;">Full Transcript</h3>
                        <div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6; color: #374151;">
{call.transcript or 'No transcript available'}
                        </div>
                    </div>

                    <div style="text-align: center;">
                        <a href="https://admin.deskringer.com/calls" class="btn">
                            View in Dashboard →
                        </a>
                    </div>
                </div>

                <div class="footer">
                    <p>Sent by DeskRinger AI Receptionist</p>
                    <p>Manage notification settings in your <a href="https://admin.deskringer.com">admin dashboard</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def generate_summary(self, customer, call):
        """
        Generate a brief AI summary of what the caller wanted
        Uses the notification_instructions to format appropriately
        """
        # TODO: Could use GPT to generate a smart summary
        # For now, use a simple heuristic

        transcript = call.transcript or ""

        # Simple summary based on first caller message
        lines = transcript.split('\n')
        caller_messages = [line for line in lines if line.startswith('Caller:')]

        if caller_messages:
            first_message = caller_messages[0].replace('Caller:', '').strip()
            return f"Caller said: {first_message[:200]}"

        return "Call received - check transcript for details"
