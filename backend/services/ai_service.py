"""
AI Service using OpenAI GPT-4 and Text-to-Speech

BALANCED OPTIMIZATION FOR QUALITY + SPEED:
- gpt-4o-mini: 50% faster than gpt-4o, 80% cheaper
- max_tokens=85: Allows complete responses
- temperature=0.5: Natural variety in responses
- speechTimeout=1.5s: Gives caller time to finish speaking
- Natural fillers: "Sure", "Let me check" - sounds human
- TTS speed=0.95: Slower, more conversational pacing

Expected latency: 4-6s with good conversation quality
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
        # Build optimized system prompt (shorter = faster processing)
        system_prompt = f"""You're the receptionist at {customer.business_name}.

{customer.ai_instructions or 'Answer questions, take messages, help with appointments.'}

Rules:
- Reply in 1 short sentence
- Sound natural and conversational - use casual language
- Start responses with natural fillers like "Sure", "Of course", "Let me check", "Absolutely"
- Never repeat questions caller already answered
- Be warm and friendly like talking to a neighbor
- If they want callback: get name + phone, say you'll have someone call them back soon"""

        # Build conversation messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": caller_message})

        # Get response from GPT-4o-mini (optimized for speed)
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # 50% faster than gpt-4o, 80% cheaper, still high quality
            messages=messages,
            temperature=0.5,  # Balanced for natural variety
            max_tokens=85,  # Allows complete responses without cutting off
            presence_penalty=0.3  # Reduce repetition
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
            model="tts-1",  # Fastest TTS model (tts-1-hd is slower but higher quality)
            voice="nova",  # Natural-sounding female voice
            input=text,
            response_format="mp3",
            speed=0.95  # Slightly slower - sounds more natural and conversational, masks latency
        )

        return response.content  # Binary MP3 audio data
