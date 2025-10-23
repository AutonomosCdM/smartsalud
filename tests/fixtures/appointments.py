"""
Appointment fixtures for testing.
"""
from datetime import datetime, timedelta
from src.database.models import Appointment, AppointmentStatus


def create_test_appointment(patient_id: int, **kwargs) -> Appointment:
    """
    Create a test appointment with default values.

    Can override any field via kwargs.
    """
    defaults = {
        "patient_id": patient_id,
        "appointment_date": datetime.now() + timedelta(days=1),
        "doctor_name": "Dr. García",
        "specialty": "Medicina General",
        "status": AppointmentStatus.PENDING,
        "notes": "Consulta de control"
    }
    defaults.update(kwargs)
    return Appointment(**defaults)


# Test appointment scenarios
TEST_APPOINTMENTS = {
    "tomorrow": {
        "appointment_date": datetime.now() + timedelta(days=1),
        "doctor_name": "Dr. García",
        "specialty": "Medicina General",
        "status": AppointmentStatus.PENDING
    },
    "next_week": {
        "appointment_date": datetime.now() + timedelta(days=7),
        "doctor_name": "Dr. Rodríguez",
        "specialty": "Cardiología",
        "status": AppointmentStatus.PENDING
    },
    "confirmed": {
        "appointment_date": datetime.now() + timedelta(days=2),
        "doctor_name": "Dr. López",
        "specialty": "Pediatría",
        "status": AppointmentStatus.CONFIRMED
    }
}
