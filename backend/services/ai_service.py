"""
AI Service using OpenAI GPT-4 and Text-to-Speech
"""
import os
from openai import OpenAI


class AIService:
    """Handle AI conversations with OpenAI"""

    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def get_response(self, customer, caller_message, conversation_history=None):
        """
        Get AI response for caller's message

        Args:
            customer: Customer object with business info and AI instructions
            caller_message: What the caller just said
            conversation_history: List of previous messages in this call

        Returns:
            AI's response text
        """
        # Build system prompt
        system_prompt = f"""You are an AI receptionist for {customer.business_name}.

Business Type: {customer.business_type or 'General business'}

{customer.ai_instructions or 'Be helpful, friendly, and professional. Answer questions about the business, take messages, and help schedule appointments.'}

IMPORTANT INSTRUCTIONS:
- Keep responses natural, conversational, and brief (1-2 sentences). Sound like a real person, not a robot.
- Pay close attention to what the caller has ALREADY told you in this conversation.
- NEVER ask for information the caller has already provided.
- If the caller gives you multiple pieces of information at once (name, phone, request), acknowledge ALL of it.
- If someone wants to schedule an appointment or needs a callback, collect their name and phone number, then confirm you'll have someone reach out.
- If they've already given you their information, don't ask for it again - just confirm and wrap up the call."""

        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": caller_message})

        # Get response from GPT-4
        response = self.client.chat.completions.create(
            model="gpt-4o",  # Latest GPT-4 model
            messages=messages,
            temperature=0.5,  # Lower temp for faster, more deterministic responses
            max_tokens=100  # Keep responses very concise for speed
        )

        ai_response = response.choices[0].message.content

        return ai_response

    def text_to_speech(self, text):
        """
        Convert text to natural-sounding speech using OpenAI TTS

        Args:
            text: Text to convert to speech

        Returns:
            Audio data (MP3 format)
        """
        response = self.client.audio.speech.create(
            model="tts-1",  # Fast model (tts-1-hd is slower but higher quality)
            voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            response_format="mp3",
            speed=1.1  # Slightly faster speech (1.0 is normal, max is 4.0)
        )

        return response.content  # Binary MP3 audio data
