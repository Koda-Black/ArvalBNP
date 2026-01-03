"""
Appointment data models for Arval BNP Voice Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class AppointmentType(Enum):
    """Types of appointments that can be booked."""
    MOT = "MOT"
    SERVICE = "Service"
    INSPECTION = "Inspection"
    FLEET_CONSULTATION = "Fleet Consultation"
    SALES_DEMO = "Sales Demo"
    ONBOARDING = "Driver Onboarding"


class TimeSlot(Enum):
    """Available time slots for appointments."""
    MORNING = "Morning (9-12)"
    AFTERNOON = "Afternoon (12-3)"
    LATE_AFTERNOON = "Late Afternoon (3-5)"


class AppointmentStatus(Enum):
    """Status of an appointment."""
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    RESCHEDULED = "Rescheduled"
    NO_SHOW = "No Show"


@dataclass
class Appointment:
    """
    Represents an appointment booking in the Arval system.
    """
    id: str
    customer_name: str
    contact_phone: str
    contact_email: str
    appointment_type: AppointmentType
    date: str  # YYYY-MM-DD format
    time_slot: TimeSlot
    status: AppointmentStatus = AppointmentStatus.PENDING
    vehicle_registration: Optional[str] = None
    additional_notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert appointment to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "appointment_type": self.appointment_type.value,
            "date": self.date,
            "time_slot": self.time_slot.value,
            "status": self.status.value,
            "vehicle_registration": self.vehicle_registration,
            "additional_notes": self.additional_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Appointment":
        """Create an Appointment instance from a dictionary."""
        return cls(
            id=data["id"],
            customer_name=data["customer_name"],
            contact_phone=data["contact_phone"],
            contact_email=data["contact_email"],
            appointment_type=AppointmentType(data["appointment_type"]),
            date=data["date"],
            time_slot=TimeSlot(data["time_slot"]),
            status=AppointmentStatus(data.get("status", "Pending")),
            vehicle_registration=data.get("vehicle_registration"),
            additional_notes=data.get("additional_notes"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            confirmed_at=datetime.fromisoformat(data["confirmed_at"]) if data.get("confirmed_at") else None,
            cancelled_at=datetime.fromisoformat(data["cancelled_at"]) if data.get("cancelled_at") else None,
            cancellation_reason=data.get("cancellation_reason"),
        )

    def confirm(self) -> None:
        """Confirm the appointment."""
        self.status = AppointmentStatus.CONFIRMED
        self.confirmed_at = datetime.now()
        self.updated_at = datetime.now()

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the appointment."""
        self.status = AppointmentStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.cancellation_reason = reason
        self.updated_at = datetime.now()

    def reschedule(self, new_date: str, new_time_slot: TimeSlot) -> None:
        """Reschedule the appointment to a new date and time."""
        self.date = new_date
        self.time_slot = new_time_slot
        self.status = AppointmentStatus.RESCHEDULED
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Mark the appointment as completed."""
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.now()

    def is_upcoming(self) -> bool:
        """Check if the appointment is upcoming (not cancelled or completed)."""
        return self.status in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.RESCHEDULED,
        ]

    def get_display_summary(self) -> str:
        """Get a human-readable summary of the appointment."""
        return (
            f"Appointment {self.id}\n"
            f"Type: {self.appointment_type.value}\n"
            f"Date: {self.date}\n"
            f"Time: {self.time_slot.value}\n"
            f"Status: {self.status.value}\n"
            f"Customer: {self.customer_name}\n"
            f"Phone: {self.contact_phone}"
        )
