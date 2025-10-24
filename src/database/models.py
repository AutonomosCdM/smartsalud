"""
SQLAlchemy models for smartSalud_V2.

Clean schema without any legacy Cal.com references.
"""
from datetime import datetime, time
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Text, Time,
    ForeignKey, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import Optional, List


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class AppointmentStatus(str, PyEnum):
    """Appointment status enum."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    COMPLETED = "COMPLETED"
    NO_SHOW = "NO_SHOW"


class Patient(Base):
    """
    Patient model.

    Represents a patient in the system with contact information.
    """
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rut: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        cascade="all, delete-orphan"
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        back_populates="patient",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, rut={self.rut}, name={self.first_name} {self.last_name})>"


class Doctor(Base):
    """
    Doctor model.

    Represents medical staff with their specialties and calendar information.
    """
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sector: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    calendar_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Google Calendar email for sync"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    schedules: Mapped[List["DoctorSchedule"]] = relationship(
        "DoctorSchedule",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor"
    )

    @property
    def name(self) -> str:
        """Full name of the doctor."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Doctor(id={self.id}, name={self.first_name} {self.last_name}, specialty={self.specialty})>"


class AppointmentType(Base):
    """
    AppointmentType model.

    Represents different types of medical services with their durations.
    """
    __tablename__ = "appointment_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Color for calendar display"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    schedules: Mapped[List["DoctorSchedule"]] = relationship(
        "DoctorSchedule",
        back_populates="appointment_type"
    )
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment",
        back_populates="appointment_type"
    )

    def __repr__(self) -> str:
        return f"<AppointmentType(id={self.id}, name={self.name}, duration={self.duration_minutes}min)>"


class DoctorSchedule(Base):
    """
    DoctorSchedule model.

    Represents recurring weekly schedule blocks for doctors.
    """
    __tablename__ = "doctor_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="0=Monday, 6=Sunday"
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    appointment_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("appointment_types.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
    appointment_type: Mapped["AppointmentType"] = relationship(
        "AppointmentType",
        back_populates="schedules"
    )

    # Composite index for common query patterns
    __table_args__ = (
        Index("ix_doctor_schedules_doctor_day", "doctor_id", "day_of_week"),
        Index("ix_doctor_schedules_time_range", "start_time", "end_time"),
    )

    def __repr__(self) -> str:
        return f"<DoctorSchedule(id={self.id}, doctor_id={self.doctor_id}, day={self.day_of_week}, {self.start_time}-{self.end_time})>"


class Appointment(Base):
    """
    Appointment model.

    Represents a medical appointment with scheduling details.
    NO Cal.com integration - uses only Google Calendar.
    """
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    doctor_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("doctors.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    appointment_type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("appointment_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    appointment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    doctor_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Deprecated: use doctor_id instead"
    )
    specialty: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus),
        nullable=False,
        default=AppointmentStatus.PENDING,
        index=True
    )
    calendar_event_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        comment="Google Calendar event ID"
    )
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped[Optional["Doctor"]] = relationship("Doctor", back_populates="appointments")
    appointment_type: Mapped[Optional["AppointmentType"]] = relationship(
        "AppointmentType",
        back_populates="appointments"
    )
    interactions: Mapped[List["Interaction"]] = relationship(
        "Interaction",
        back_populates="appointment",
        cascade="all, delete-orphan"
    )

    # Composite index for common query pattern
    __table_args__ = (
        Index("ix_appointments_date_status", "appointment_date", "status"),
    )

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, date={self.appointment_date}, status={self.status})>"


class Interaction(Base):
    """
    Interaction model.

    Audit log of WhatsApp message interactions with NLP detection results.
    """
    __tablename__ = "interactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    appointment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("appointments.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    message_from: Mapped[str] = mapped_column(String(30), nullable=False)
    message_to: Mapped[str] = mapped_column(String(30), nullable=False)
    message_body: Mapped[str] = mapped_column(Text, nullable=False)
    detected_intent: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="NLP detected intent (CONFIRM/CANCEL/UNKNOWN)"
    )
    confidence_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="NLP confidence score 0-100"
    )
    twilio_message_sid: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        comment="Twilio Message SID for deduplication"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP",
        index=True  # Index for audit queries
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default="CURRENT_TIMESTAMP"
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="interactions")
    appointment: Mapped[Optional["Appointment"]] = relationship(
        "Appointment",
        back_populates="interactions"
    )

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, patient_id={self.patient_id}, intent={self.detected_intent})>"
