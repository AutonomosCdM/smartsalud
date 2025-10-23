"""
Intent enumeration for WhatsApp messages.
"""
from enum import Enum


class Intent(str, Enum):
    """Possible user intents."""

    CONFIRM = "confirm"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


class IntentResult:
    """Result of intent detection."""

    def __init__(self, intent: Intent, confidence: float):
        self.intent = intent
        self.confidence = confidence

    def __repr__(self):
        return f"IntentResult(intent={self.intent}, confidence={self.confidence})"
