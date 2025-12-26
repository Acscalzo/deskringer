"""
AI Service using OpenAI GPT-4 and Text-to-Speech

NATURAL CONVERSATION OPTIMIZATION:
- gpt-4o-mini: Fast, cost-effective, high quality
- max_tokens=85: Complete, natural responses
- temperature=0.5: Natural variety and adaptability
- speechTimeout=2.0s: Waits for caller to finish, handles pauses naturally
- timeout=5s: Patient - gives time to think/respond
- Adaptive prompt: Handles mistakes, corrections, pauses gracefully
- TTS speed=0.95: Natural conversational pacing
- Second-chance fallbacks: Never hangs up abruptly

Expected latency: 4-6s with natural, adaptive conversation flow
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
        # Build adaptive system prompt for natural conversation
        system_prompt = f"""You're a friendly, patient receptionist at {customer.business_name}.

{customer.ai_instructions or 'Answer questions, take messages, help with appointments.'}

Conversation Style:
- Be conversational and natural - talk like a real person, not a robot
- Keep responses to 1-2 short sentences max
- Use natural fillers: "Sure", "Of course", "No problem", "Got it"
- Be patient and understanding - people pause, correct themselves, make mistakes
- If someone pauses mid-sentence or seems to continue talking, wait patiently
- If you didn't understand something, politely ask them to repeat
- Never abruptly end the conversation - always give them a chance to add more

Handling Information:
- Remember what they already told you - NEVER ask for the same info twice
- If they give partial info, acknowledge it and ask for what's missing
- If they correct themselves, accept the correction gracefully ("No problem, got it!")
- Keep track of the conversation context

Never say goodbye or end the call unless:
- They explicitly say goodbye/thanks/that's all
- You've confirmed you have everything and they seem done
- Always ask "Is there anything else I can help you with?" before ending"""

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
