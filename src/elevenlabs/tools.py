"""
ElevenLabs Agent Tools - Function calling endpoints

These endpoints are called by the ElevenLabs conversational AI agent
during the conversation with the patient.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.database.connection import get_db
from src.database.models import Patient, Appointment, Doctor
from src.services.booking_service import BookingService
from src.services.availability_service_v2 import AvailabilityServiceV2
from src.whatsapp.service import send_whatsapp_message
from src.calendar.service import CalendarService

router = APIRouter(prefix="/api/elevenlabs/tools", tags=["elevenlabs"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class GetAppointmentRequest(BaseModel):
    rut: str

class GetAppointmentResponse(BaseModel):
    found: bool
    appointment_id: int | None = None
    patient_name: str | None = None
    doctor_name: str | None = None
    appointment_date: str | None = None
    appointment_type: str | None = None
    status: str | None = None

class GetSlotsRequest(BaseModel):
    doctor_id: int
    date: str | None = None  # Optional: defaults to tomorrow

class SlotInfo(BaseModel):
    datetime: str
    doctor_name: str
    available: bool

class GetSlotsResponse(BaseModel):
    slots: List[SlotInfo]

class RescheduleRequest(BaseModel):
    appointment_id: int
    new_datetime: str  # Format: "YYYY-MM-DD HH:MM"

class RescheduleResponse(BaseModel):
    success: bool
    message: str
    new_appointment_date: str | None = None
    calendar_updated: bool = False

class EndConversationRequest(BaseModel):
    patient_rut: str
    summary: str

class EndConversationResponse(BaseModel):
    whatsapp_sent: bool
    message: str


# ============================================================================
# TOOL ENDPOINTS
# ============================================================================

@router.post("/get_appointment", response_model=GetAppointmentResponse)
async def get_patient_appointment(
    request: GetAppointmentRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Busca la próxima cita del paciente por RUT.

    El agente usa esto para obtener información de la cita actual del paciente.
    """
    # Find patient
    result = await session.execute(
        select(Patient).where(Patient.rut == request.rut)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        return GetAppointmentResponse(found=False)

    # Find next pending appointment
    result = await session.execute(
        select(Appointment)
        .where(
            Appointment.patient_id == patient.id,
            Appointment.status == "PENDING",
            Appointment.appointment_date > datetime.now()
        )
        .order_by(Appointment.appointment_date)
    )
    appointment = result.scalar_one_or_none()

    if not appointment:
        return GetAppointmentResponse(found=False)

    # Get doctor info
    doctor = await session.get(Doctor, appointment.doctor_id)

    return GetAppointmentResponse(
        found=True,
        appointment_id=appointment.id,
        patient_name=f"{patient.first_name} {patient.last_name}",
        doctor_name=doctor.name if doctor else "Doctor",
        appointment_date=appointment.appointment_date.strftime("%Y-%m-%d %H:%M"),
        appointment_type=appointment.appointment_type.name if appointment.appointment_type else "Consulta",
        status=appointment.status
    )


@router.post("/get_slots", response_model=GetSlotsResponse)
async def get_available_slots(
    request: GetSlotsRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Obtiene horarios disponibles para reagendar.

    El agente usa esto para ofrecer opciones al paciente.
    """
    # Default to tomorrow if no date specified
    target_date = (
        datetime.strptime(request.date, "%Y-%m-%d").date()
        if request.date
        else (datetime.now() + timedelta(days=1)).date()
    )

    # Get doctor
    doctor = await session.get(Doctor, request.doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Get availability service
    availability_service = AvailabilityServiceV2(session)

    # Get available slots for the day
    slots = await availability_service.get_available_slots(
        doctor_id=request.doctor_id,
        date=target_date
    )

    # Format response
    slot_infos = [
        SlotInfo(
            datetime=slot['start_time'].strftime("%Y-%m-%d %H:%M"),
            doctor_name=doctor.name,
            available=True
        )
        for slot in slots[:10]  # Limit to 10 slots
    ]

    return GetSlotsResponse(slots=slot_infos)


@router.post("/reschedule", response_model=RescheduleResponse)
async def reschedule_appointment(
    request: RescheduleRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Reagenda una cita a una nueva fecha/hora.

    IMPORTANTE: Esto actualiza la base de datos Y el Google Calendar en tiempo real.
    El agente llama esto cuando el paciente confirma el cambio de hora.
    """
    try:
        # Get appointment
        appointment = await session.get(Appointment, request.appointment_id)
        if not appointment:
            return RescheduleResponse(
                success=False,
                message="Cita no encontrada"
            )

        # Parse new datetime
        new_datetime = datetime.strptime(request.new_datetime, "%Y-%m-%d %H:%M")

        # Get booking service
        booking_service = BookingService(session)
        calendar_service = CalendarService()

        # Update appointment
        appointment.appointment_date = new_datetime
        appointment.status = "CONFIRMED"  # Auto-confirm when rescheduled via agent
        appointment.updated_at = datetime.now()

        await session.commit()
        await session.refresh(appointment)

        # Update Google Calendar
        calendar_updated = False
        if appointment.calendar_event_id:
            try:
                # Get doctor
                doctor = await session.get(Doctor, appointment.doctor_id)

                await calendar_service.update_event(
                    event_id=appointment.calendar_event_id,
                    start_time=new_datetime,
                    end_time=new_datetime + timedelta(minutes=appointment.appointment_type.duration_minutes),
                    summary=f"[CONFIRMADA] {appointment.patient.first_name} {appointment.patient.last_name}",
                    description=f"Cita reagendada via agente de voz\n\nDoctor: {doctor.name}\nPaciente: {appointment.patient.first_name} {appointment.patient.last_name}\nRUT: {appointment.patient.rut}",
                    calendar_email=doctor.calendar_email if doctor else None
                )
                calendar_updated = True
            except Exception as e:
                print(f"Error updating calendar: {e}")

        return RescheduleResponse(
            success=True,
            message=f"Cita reagendada exitosamente para {new_datetime.strftime('%d/%m/%Y a las %H:%M')}",
            new_appointment_date=new_datetime.strftime("%Y-%m-%d %H:%M"),
            calendar_updated=calendar_updated
        )

    except ValueError as e:
        return RescheduleResponse(
            success=False,
            message=f"Formato de fecha inválido: {str(e)}"
        )
    except Exception as e:
        return RescheduleResponse(
            success=False,
            message=f"Error al reagendar: {str(e)}"
        )


@router.post("/end_conversation", response_model=EndConversationResponse)
async def end_conversation(
    request: EndConversationRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Finaliza la conversación y envía confirmación por WhatsApp.

    El agente llama esto al terminar la conversación para que el paciente
    reciba un mensaje de WhatsApp con el resumen.
    """
    try:
        # Find patient
        result = await session.execute(
            select(Patient).where(Patient.rut == request.patient_rut)
        )
        patient = result.scalar_one_or_none()

        if not patient:
            return EndConversationResponse(
                whatsapp_sent=False,
                message="Paciente no encontrado"
            )

        # Send WhatsApp confirmation
        message_text = f"""✅ Confirmación de Cita - CESFAM SmartSalud

Hola {patient.first_name}!

{request.summary}

Si tienes dudas, llámanos al (56) 2 1234 5678.

¡Que tengas un buen día! 🏥"""

        # Send via Twilio
        await send_whatsapp_message(
            to=patient.phone,
            body=message_text
        )

        return EndConversationResponse(
            whatsapp_sent=True,
            message="Confirmación enviada por WhatsApp"
        )

    except Exception as e:
        return EndConversationResponse(
            whatsapp_sent=False,
            message=f"Error al enviar WhatsApp: {str(e)}"
        )
