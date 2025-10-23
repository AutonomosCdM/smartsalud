"""
NLP service with Groq API and circuit breaker.

Primary: Groq API (llama-3.3-70b-versatile)
Fallback: Regex patterns
Recovery: Exponential backoff
"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from groq import AsyncGroq
import structlog

from src.core.config import settings
from src.nlp.intents import Intent, IntentResult
from src.nlp.patterns import detect_intent_regex

logger = structlog.get_logger(__name__)


class CircuitBreaker:
    """Circuit breaker for Groq API."""

    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.is_open = False

    def record_success(self):
        """Record successful API call."""
        self.failures = 0
        self.is_open = False

    def record_failure(self):
        """Record failed API call."""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.is_open = True
            logger.warning(
                "circuit_breaker_opened",
                failures=self.failures,
                recovery_timeout=self.recovery_timeout
            )

    def can_attempt(self) -> bool:
        """Check if API call can be attempted."""
        if not self.is_open:
            return True

        # Check if recovery timeout has passed
        if self.last_failure_time:
            elapsed = (datetime.now() - self.last_failure_time).seconds
            if elapsed >= self.recovery_timeout:
                logger.info("circuit_breaker_attempting_recovery")
                self.is_open = False
                self.failures = 0
                return True

        return False


class NLPService:
    """NLP service with Groq API and fallback."""

    def __init__(self):
        self.groq_client = AsyncGroq(api_key=settings.groq_api_key)
        self.circuit_breaker = CircuitBreaker()

    async def detect_intent(self, message: str) -> IntentResult:
        """
        Detect intent from user message.

        Args:
            message: User message in Spanish

        Returns:
            IntentResult with intent and confidence
        """
        # Try Groq API if circuit breaker allows
        if self.circuit_breaker.can_attempt():
            try:
                result = await self._detect_with_groq(message)
                self.circuit_breaker.record_success()
                return result
            except Exception as e:
                logger.error("groq_api_failed", error=str(e))
                self.circuit_breaker.record_failure()

        # Fallback to regex
        logger.info("using_regex_fallback")
        intent_str, confidence = detect_intent_regex(message)
        intent = Intent(intent_str)
        return IntentResult(intent=intent, confidence=confidence)

    async def _detect_with_groq(self, message: str) -> IntentResult:
        """
        Detect intent using Groq API.

        Timeout: 5 seconds
        """
        prompt = f"""Analiza este mensaje de WhatsApp y determina la intención del usuario.

Mensaje: "{message}"

Responde SOLO con una de estas opciones:
- CONFIRM (si el usuario confirma asistir a una cita)
- CANCEL (si el usuario cancela una cita)
- UNKNOWN (si no está claro)

Respuesta:"""

        response = await asyncio.wait_for(
            self.groq_client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10
            ),
            timeout=settings.groq_timeout
        )

        content = response.choices[0].message.content.strip().upper()

        # Parse response
        if "CONFIRM" in content:
            return IntentResult(intent=Intent.CONFIRM, confidence=0.9)
        elif "CANCEL" in content:
            return IntentResult(intent=Intent.CANCEL, confidence=0.9)
        else:
            return IntentResult(intent=Intent.UNKNOWN, confidence=0.5)
