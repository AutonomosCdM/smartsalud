"""
WhatsApp message templates in Spanish.

All user-facing messages for Chile.
"""


def confirmation_message(
    patient_name: str,
    appointment_date: str,
    doctor_name: str
) -> str:
    """Message sent when appointment is confirmed."""
    return f"""✅ ¡Cita CONFIRMADA!

Hola {patient_name},

Tu cita ha sido confirmada:
📅 Fecha: {appointment_date}
👨‍⚕️ Doctor(a): {doctor_name}

¡Te esperamos!

CESFAM Futrono"""


def cancellation_message(
    patient_name: str,
    appointment_date: str,
    doctor_name: str
) -> str:
    """Message sent when appointment is cancelled."""
    return f"""❌ Cita CANCELADA

Hola {patient_name},

Tu cita del {appointment_date} con {doctor_name} ha sido cancelada.

Para reagendar, comunícate con nosotros al teléfono del CESFAM.

CESFAM Futrono"""


def unknown_intent_message() -> str:
    """Message sent when intent is unclear."""
    return """🤔 No entendí tu mensaje

Por favor responde:
- "Confirmo" para confirmar tu cita
- "Cancelo" para cancelar tu cita

CESFAM Futrono"""


def reminder_message(
    patient_name: str,
    appointment_date: str,
    doctor_name: str
) -> str:
    """Reminder message sent the day before."""
    return f"""🔔 Recordatorio de Cita

Hola {patient_name},

Tienes una cita médica mañana:
📅 Fecha: {appointment_date}
👨‍⚕️ Doctor(a): {doctor_name}

Por favor confirma respondiendo:
- "Confirmo" si asistirás
- "Cancelo" si no puedes asistir

CESFAM Futrono"""


def no_appointment_message() -> str:
    """Message when no appointment found for patient."""
    return """ℹ️ No encontramos citas pendientes

No tenemos citas pendientes registradas para este número.

Si necesitas ayuda, comunícate con nosotros al teléfono del CESFAM.

CESFAM Futrono"""


def patient_not_found_message() -> str:
    """Message when patient not found in system."""
    return """ℹ️ Número no registrado

Este número no está registrado en nuestro sistema.

Por favor comunícate con el CESFAM para más información.

CESFAM Futrono"""
