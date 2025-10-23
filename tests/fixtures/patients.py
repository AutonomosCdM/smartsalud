"""
Patient fixtures for testing.

Synthetic patient data for tests.
"""
from datetime import datetime
from src.database.models import Patient


def create_test_patient(**kwargs) -> Patient:
    """
    Create a test patient with default values.

    Can override any field via kwargs.
    """
    defaults = {
        "rut": "12345678-9",
        "phone": "whatsapp:+56912345678",
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@example.com"
    }
    defaults.update(kwargs)
    return Patient(**defaults)


# Predefined test patients
TEST_PATIENTS = [
    {
        "rut": "11111111-1",
        "phone": "whatsapp:+56911111111",
        "first_name": "María",
        "last_name": "González",
        "email": "maria.gonzalez@example.com"
    },
    {
        "rut": "22222222-2",
        "phone": "whatsapp:+56922222222",
        "first_name": "Pedro",
        "last_name": "Ramírez",
        "email": "pedro.ramirez@example.com"
    },
    {
        "rut": "33333333-3",
        "phone": "whatsapp:+56933333333",
        "first_name": "Ana",
        "last_name": "Silva",
        "email": "ana.silva@example.com"
    }
]
