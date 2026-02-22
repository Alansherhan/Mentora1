"""
AI Service Module for Mentora
Integrates Groq AI (with Llama models) as a smart fallback for unanswered queries.
Falls back to Google Gemini if Groq is unavailable.
"""

import os
import time
from typing import Dict, Any, Optional, List

# Try to import Groq SDK
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq not installed. Install with: pip install groq")

# Try to import Google GenAI (fallback)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# System prompt that defines Mentora's AI personality
SYSTEM_PROMPT = """You are Mentora, an AI-powered college assistant chatbot. You help students with:
- Academic questions and explanations
- Study tips and learning strategies
- General knowledge questions
- Career guidance and advice
- Technology and programming help

IMPORTANT GUIDELINES:
1. Keep responses concise and student-friendly (2-4 paragraphs max)
2. Use simple, clear language
3. If a question is about specific college info (fees, teachers, timetable), say you don't have that specific info and suggest they ask the admin
4. Be encouraging and supportive
5. Use emojis sparingly to keep a friendly tone
6. Never generate harmful, inappropriate, or misleading content
7. For mental health concerns, be empathetic but recommend professional help for serious issues
8. Format responses with clear structure when explaining concepts
"""


class AIService:
    """Handles AI-powered responses using Groq (primary) and Gemini (fallback)"""

    # Groq models to try (free tier, very fast)
    GROQ_MODELS = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "gemma2-9b-it",
    ]

    # Gemini models (fallback)
    GEMINI_MODELS = [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ]

    def __init__(self, groq_api_key: str = None, gemini_api_key: str = None):
        """
        Initialize the AI service with Groq as primary and Gemini as fallback.

        Args:
            groq_api_key: Groq API key. If not provided, reads from GROQ_API_KEY env var.
            gemini_api_key: Gemini API key (fallback). Reads from GEMINI_API_KEY env var.
        """
        self.enabled = False
        self.groq_client = None
        self.gemini_client = None
        self.last_request_time = 0
        self.min_request_interval = 2  # seconds between requests

        # Conversation history per session
        self.conversations: Dict[str, List[Dict]] = {}

        # Initialize Groq (primary)
        groq_key = groq_api_key or os.environ.get('GROQ_API_KEY', '')
        if groq_key and GROQ_AVAILABLE:
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.enabled = True
                print("AI Service: ✅ Groq AI initialized (primary)")
            except Exception as e:
                print(f"AI Service: Failed to initialize Groq: {e}")

        # Initialize Gemini (fallback)
        gemini_key = gemini_api_key or os.environ.get('GEMINI_API_KEY', '')
        if gemini_key and GENAI_AVAILABLE:
            try:
                self.gemini_client = genai.Client(api_key=gemini_key)
                if not self.enabled:
                    self.enabled = True
                print("AI Service: ✅ Gemini AI initialized (fallback)")
            except Exception as e:
                print(f"AI Service: Failed to initialize Gemini: {e}")

        if not self.enabled:
            print("AI Service: ⚠️ No AI providers available. Set GROQ_API_KEY or GEMINI_API_KEY.")
            print("AI Service: Get free Groq key at https://console.groq.com")

    def _rate_limit(self):
        """Enforce rate limiting"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _try_groq(self, query: str, session_id: str) -> Optional[str]:
        """Try to get response from Groq"""
        if not self.groq_client:
            return None

        # Build messages with history
        history = self.conversations.get(session_id, [])
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["text"]
            })

        messages.append({"role": "user", "content": query})

        # Try each Groq model
        for model_name in self.GROQ_MODELS:
            try:
                print(f"AI Service: Trying Groq/{model_name}...")
                response = self.groq_client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7,
                )
                result = response.choices[0].message.content
                print(f"AI Service: ✅ Got response from Groq/{model_name}")
                return result

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    print(f"AI Service: Groq/{model_name} rate limited, trying next...")
                    continue
                else:
                    print(f"AI Service: Groq/{model_name} error: {e}")
                    continue

        return None

    def _try_gemini(self, query: str, session_id: str) -> Optional[str]:
        """Try to get response from Gemini (fallback)"""
        if not self.gemini_client:
            return None

        # Build contents with history
        history = self.conversations.get(session_id, [])
        contents = []

        for msg in history:
            contents.append(types.Content(
                role=msg["role"] if msg["role"] != "assistant" else "model",
                parts=[types.Part.from_text(text=msg["text"])]
            ))

        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=query)]
        ))

        # Try each Gemini model
        for model_name in self.GEMINI_MODELS:
            try:
                print(f"AI Service: Trying Gemini/{model_name}...")
                response = self.gemini_client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=500,
                        temperature=0.7,
                    )
                )
                result = response.text
                print(f"AI Service: ✅ Got response from Gemini/{model_name}")
                return result

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"AI Service: Gemini/{model_name} quota exhausted, trying next...")
                    continue
                else:
                    print(f"AI Service: Gemini/{model_name} error: {e}")
                    continue

        return None

    def generate_response(self, query: str, session_id: str = "default") -> Optional[str]:
        """
        Generate an AI response. Tries Groq first, then Gemini as fallback.

        Args:
            query: The user's question/message
            session_id: Session identifier for conversation history

        Returns:
            AI-generated response string, or None if all providers fail
        """
        if not self.enabled:
            return None

        self._rate_limit()

        # Try Groq first (faster, free)
        response_text = self._try_groq(query, session_id)

        # Fall back to Gemini
        if not response_text:
            response_text = self._try_gemini(query, session_id)

        # Store conversation history
        if response_text:
            if session_id not in self.conversations:
                self.conversations[session_id] = []

            self.conversations[session_id].append({
                "role": "user",
                "text": query
            })
            self.conversations[session_id].append({
                "role": "assistant",
                "text": response_text
            })

            # Trim history
            if len(self.conversations[session_id]) > 20:
                self.conversations[session_id] = self.conversations[session_id][-20:]

        return response_text

    def clear_conversation(self, session_id: str = "default"):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]

    def is_available(self) -> bool:
        """Check if AI service is available and configured"""
        return self.enabled
