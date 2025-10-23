"""
Regex patterns for Spanish (Chilean) intent detection.

Used as fallback when Groq API fails.
"""
import re

# Confirmation patterns (Chilean Spanish)
CONFIRM_PATTERNS = [
    r"\bconfirmo\b",
    r"\bconfirmar\b",
    r"\bsí\b",
    r"\bsi\b",
    r"\bok\b",
    r"\bacepto\b",
    r"\bvoy\b",
    r"\basisto\b",
    r"\basistiré\b",
    r"\bestoy\b",
    r"\biré\b",
]

# Cancellation patterns (Chilean Spanish)
CANCEL_PATTERNS = [
    r"\bcancelo\b",
    r"\bcancelar\b",
    r"\bno puedo\b",
    r"\bno voy\b",
    r"\bno asistiré\b",
    r"\bno asisto\b",
    r"\bno iré\b",
    r"\banular\b",
]


def detect_intent_regex(message: str) -> tuple[str, float]:
    """
    Detect intent using regex patterns.

    Args:
        message: User message in Spanish

    Returns:
        Tuple of (intent, confidence)
        Confidence is always 0.7 for regex matches
    """
    message_lower = message.lower()

    # Check confirmation patterns
    for pattern in CONFIRM_PATTERNS:
        if re.search(pattern, message_lower):
            return ("confirm", 0.7)

    # Check cancellation patterns
    for pattern in CANCEL_PATTERNS:
        if re.search(pattern, message_lower):
            return ("cancel", 0.7)

    # Unknown intent
    return ("unknown", 0.3)
