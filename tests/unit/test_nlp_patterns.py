"""
Unit tests for NLP regex patterns.
"""
import pytest
from src.nlp.patterns import detect_intent_regex


class TestNLPPatterns:
    """Test regex pattern matching for intent detection."""

    def test_confirm_patterns(self):
        """Test confirmation pattern detection."""
        test_cases = [
            ("Confirmo", "confirm"),
            ("Sí, confirmo mi cita", "confirm"),
            ("Ok, voy", "confirm"),
            ("Asistiré", "confirm"),
            ("Si, iré", "confirm"),
        ]

        for message, expected_intent in test_cases:
            intent, confidence = detect_intent_regex(message)
            assert intent == expected_intent
            assert confidence == 0.7

    def test_cancel_patterns(self):
        """Test cancellation pattern detection."""
        test_cases = [
            ("Cancelo", "cancel"),
            ("No puedo asistir", "cancel"),
            ("No voy a ir", "cancel"),
            ("Quiero cancelar", "cancel"),
            ("No asistiré", "cancel"),
        ]

        for message, expected_intent in test_cases:
            intent, confidence = detect_intent_regex(message)
            assert intent == expected_intent
            assert confidence == 0.7

    def test_unknown_patterns(self):
        """Test unknown intent detection."""
        test_cases = [
            "Hola",
            "¿Qué hora es mi cita?",
            "Necesito información",
            "Gracias",
        ]

        for message in test_cases:
            intent, confidence = detect_intent_regex(message)
            assert intent == "unknown"
            assert confidence == 0.3
