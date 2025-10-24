"""
Distribuir citas para pacientes ficticios con diferentes estados y colores
"""
import asyncio
from datetime import datetime, timedelta
from sqlalchemy import select, delete

from src.database.connection import get_session_factory
from src.database.models import Patient, Doctor, Appointment, AppointmentType

async def distribute_appointments():
    """
    Crear citas variadas con diferentes estados:
    - PENDING (Amarillo #FBD75B)
    - CONFIRMED (Verde #7AE7BF)
    - CANCELLED (Rojo #F06292)
    """

    session_factory = get_session_factory()
    async with session_factory() as session:

        # 1. Limpiar citas existentes
        await session.execute(delete(Appointment))
        await session.commit()
        print("✅ Citas anteriores eliminadas")

        # 2. Obtener pacientes
        result = await session.execute(select(Patient))
        patients = list(result.scalars().all())
        print(f"📋 {len(patients)} pacientes encontrados")

        # 3. Obtener doctores
        result = await session.execute(select(Doctor))
        doctors = list(result.scalars().all())
        print(f"👨‍⚕️ {len(doctors)} doctores encontrados")

        # 4. Obtener tipos de citas
        result = await session.execute(select(AppointmentType))
        apt_types = list(result.scalars().all())
        print(f"📅 {len(apt_types)} tipos de citas encontrados\n")

        # 5. Crear citas variadas
        base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        appointments_data = [
            # Lunes 28/10 - Mix de estados
            {
                "patient": patients[0],  # María González
                "doctor": doctors[0],    # Jordi Opazo
                "apt_type": apt_types[0], # Cons. Morbilidad
                "date": base_date + timedelta(days=5, hours=0),  # 9:00 AM
                "status": "CONFIRMED",
                "notes": "Confirmada - Control de rodilla"
            },
            {
                "patient": patients[1],  # Sandra Castillo
                "doctor": doctors[1],    # María González
                "apt_type": apt_types[2], # Control crónico
                "date": base_date + timedelta(days=5, hours=2),  # 11:00 AM
                "status": "PENDING",
                "notes": "Pendiente de confirmación - Control diabetes"
            },

            # Martes 29/10 - Más variedad
            {
                "patient": patients[2],  # Americo Gonzales
                "doctor": doctors[2],    # Pedro Ramírez
                "apt_type": apt_types[1], # Salud Mental
                "date": base_date + timedelta(days=6, hours=1),  # 10:00 AM
                "status": "CONFIRMED",
                "notes": "Confirmada - Evaluación pediátrica"
            },
            {
                "patient": patients[3],  # Patricio Contreras
                "doctor": doctors[3],    # Ana Torres
                "apt_type": apt_types[0], # Cons. Morbilidad
                "date": base_date + timedelta(days=6, hours=4),  # 1:00 PM
                "status": "CANCELLED",
                "notes": "Cancelada por el paciente"
            },

            # Miércoles 30/10 - Confirmadas
            {
                "patient": patients[0],  # María González
                "doctor": doctors[2],    # Pedro Ramírez
                "apt_type": apt_types[4], # Recetas
                "date": base_date + timedelta(days=7, hours=0),  # 9:00 AM
                "status": "CONFIRMED",
                "notes": "Confirmada - Renovación de recetas"
            },
            {
                "patient": patients[1],  # Sandra Castillo
                "doctor": doctors[0],    # Jordi Opazo
                "apt_type": apt_types[0], # Cons. Morbilidad
                "date": base_date + timedelta(days=7, hours=3),  # 12:00 PM
                "status": "CONFIRMED",
                "notes": "Confirmada - Terapia física"
            },

            # Jueves 31/10 - Pendientes
            {
                "patient": patients[2],  # Americo Gonzales
                "doctor": doctors[1],    # María González
                "apt_type": apt_types[2], # Control crónico
                "date": base_date + timedelta(days=8, hours=1),  # 10:00 AM
                "status": "PENDING",
                "notes": "Pendiente - Control hipertensión"
            },
            {
                "patient": patients[3],  # Patricio Contreras
                "doctor": doctors[0],    # Jordi Opazo
                "apt_type": apt_types[0], # Cons. Morbilidad
                "date": base_date + timedelta(days=8, hours=5),  # 2:00 PM
                "status": "PENDING",
                "notes": "Pendiente - Primera consulta"
            },

            # Viernes 01/11 - Mix final
            {
                "patient": patients[0],  # María González
                "doctor": doctors[3],    # Ana Torres
                "apt_type": apt_types[1], # Salud Mental
                "date": base_date + timedelta(days=9, hours=2),  # 11:00 AM
                "status": "RESCHEDULED",
                "notes": "Reagendada - Cambiada de horario por paciente"
            },
            {
                "patient": patients[1],  # Sandra Castillo
                "doctor": doctors[2],    # Pedro Ramírez
                "apt_type": apt_types[3], # Pausa Saludable
                "date": base_date + timedelta(days=9, hours=4),  # 1:00 PM
                "status": "CANCELLED",
                "notes": "Cancelada - Conflicto de horario"
            },

            # Lunes siguiente - Semana adicional
            {
                "patient": patients[2],  # Americo Gonzales
                "doctor": doctors[3],    # Ana Torres
                "apt_type": apt_types[2], # Control crónico
                "date": base_date + timedelta(days=12, hours=0),  # 9:00 AM
                "status": "PENDING",
                "notes": "Pendiente - Control mensual"
            },
            {
                "patient": patients[3],  # Patricio Contreras
                "doctor": doctors[1],    # María González
                "apt_type": apt_types[4], # Recetas
                "date": base_date + timedelta(days=12, hours=3),  # 12:00 PM
                "status": "CONFIRMED",
                "notes": "Confirmada - Recetas crónicas"
            },
        ]

        # 6. Crear citas
        print("Creando citas:\n")
        for apt_data in appointments_data:
            appointment = Appointment(
                patient_id=apt_data["patient"].id,
                doctor_id=apt_data["doctor"].id,
                appointment_type_id=apt_data["apt_type"].id,
                appointment_date=apt_data["date"],
                doctor_name=f"{apt_data['doctor'].first_name} {apt_data['doctor'].last_name}",
                specialty=apt_data["doctor"].specialty,
                status=apt_data["status"],
                notes=apt_data["notes"]
            )
            session.add(appointment)
            await session.flush()

            # Emoji según estado
            emoji = {
                "CONFIRMED": "✅",
                "PENDING": "⏳",
                "CANCELLED": "❌",
                "RESCHEDULED": "🔄"
            }[apt_data["status"]]

            print(f"{emoji} {apt_data['status']:10} | {apt_data['date'].strftime('%d/%m %H:%M')} | "
                  f"{apt_data['patient'].first_name:15} → Dr. {apt_data['doctor'].first_name:12} | "
                  f"{apt_data['apt_type'].name}")

        await session.commit()

        print("\n" + "="*80)
        print("✅ DISTRIBUCIÓN COMPLETA")
        print("="*80)

        # Estadísticas
        confirmed = sum(1 for a in appointments_data if a["status"] == "CONFIRMED")
        pending = sum(1 for a in appointments_data if a["status"] == "PENDING")
        rescheduled = sum(1 for a in appointments_data if a["status"] == "RESCHEDULED")
        cancelled = sum(1 for a in appointments_data if a["status"] == "CANCELLED")

        print(f"\n📊 RESUMEN:")
        print(f"   ✅ Confirmadas:  {confirmed} (Verde #7AE7BF)")
        print(f"   ⏳ Pendientes:   {pending} (Amarillo #FBD75B)")
        print(f"   🔄 Reagendadas:  {rescheduled} (Indigo #818CF8)")
        print(f"   ❌ Canceladas:   {cancelled} (Rojo #F06292)")
        print(f"   📅 Total:        {len(appointments_data)}")

if __name__ == "__main__":
    asyncio.run(distribute_appointments())
