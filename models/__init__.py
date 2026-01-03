"""Models module for Arval BNP Voice Agent."""

from .appointment import Appointment, AppointmentType, TimeSlot, AppointmentStatus
from .lead import Lead, LeadPriority, ContactMethod

__all__ = [
    "Appointment",
    "AppointmentType",
    "TimeSlot",
    "AppointmentStatus",
    "Lead",
    "LeadPriority",
    "ContactMethod",
]
