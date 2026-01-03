"""
Unit tests for Arval BNP Voice Agent.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

# Test the tools
from agent.tools import (
    get_business_hours,
    check_after_hours,
    get_roadside_assistance,
    get_faq_answer,
)

# Test the models
from models.appointment import Appointment, AppointmentType, TimeSlot, AppointmentStatus
from models.lead import Lead, LeadPriority, LeadStatus, ContactMethod


class TestTools:
    """Tests for agent tools."""
    
    def test_get_business_hours(self):
        """Test that business hours returns expected information."""
        result = get_business_hours()
        
        assert "9:00 AM" in result
        assert "5:00 PM" in result
        assert "Monday to Friday" in result
        assert "Swindon" in result
    
    def test_get_roadside_assistance(self):
        """Test that roadside assistance provides emergency info."""
        result = get_roadside_assistance()
        
        assert "24/7" in result
        assert "Breakdown" in result or "breakdown" in result
        assert "Safety" in result
    
    def test_get_faq_answer_leasing(self):
        """Test FAQ answer for leasing topic."""
        result = get_faq_answer("leasing")
        
        assert "leasing" in result.lower()
        assert "vehicle" in result.lower() or "lease" in result.lower()
    
    def test_get_faq_answer_invalid_topic(self):
        """Test FAQ answer for invalid topic."""
        result = get_faq_answer("invalid_topic")
        
        assert "topic" in result.lower()
        assert "leasing" in result  # Should list available topics
    
    def test_get_faq_answer_all_topics(self):
        """Test that all expected FAQ topics are available."""
        topics = ["leasing", "fleet", "ev", "mot", "pricing", "contracts", "careers", "general"]
        
        for topic in topics:
            result = get_faq_answer(topic)
            assert "FAQs" in result or "Q:" in result, f"Topic '{topic}' should return FAQ content"


class TestAppointmentModel:
    """Tests for Appointment data model."""
    
    def create_test_appointment(self) -> Appointment:
        """Create a test appointment instance."""
        return Appointment(
            id="APT-TEST001",
            customer_name="John Smith",
            contact_phone="+44 1234 567890",
            contact_email="john.smith@example.com",
            appointment_type=AppointmentType.MOT,
            date="2026-02-15",
            time_slot=TimeSlot.MORNING,
        )
    
    def test_appointment_creation(self):
        """Test appointment creation with required fields."""
        apt = self.create_test_appointment()
        
        assert apt.id == "APT-TEST001"
        assert apt.customer_name == "John Smith"
        assert apt.appointment_type == AppointmentType.MOT
        assert apt.status == AppointmentStatus.PENDING
    
    def test_appointment_confirm(self):
        """Test confirming an appointment."""
        apt = self.create_test_appointment()
        apt.confirm()
        
        assert apt.status == AppointmentStatus.CONFIRMED
        assert apt.confirmed_at is not None
    
    def test_appointment_cancel(self):
        """Test cancelling an appointment."""
        apt = self.create_test_appointment()
        apt.cancel(reason="Customer request")
        
        assert apt.status == AppointmentStatus.CANCELLED
        assert apt.cancelled_at is not None
        assert apt.cancellation_reason == "Customer request"
    
    def test_appointment_reschedule(self):
        """Test rescheduling an appointment."""
        apt = self.create_test_appointment()
        apt.reschedule("2026-02-20", TimeSlot.AFTERNOON)
        
        assert apt.status == AppointmentStatus.RESCHEDULED
        assert apt.date == "2026-02-20"
        assert apt.time_slot == TimeSlot.AFTERNOON
    
    def test_appointment_to_dict(self):
        """Test converting appointment to dictionary."""
        apt = self.create_test_appointment()
        data = apt.to_dict()
        
        assert data["id"] == "APT-TEST001"
        assert data["customer_name"] == "John Smith"
        assert data["appointment_type"] == "MOT"
        assert data["time_slot"] == "Morning (9-12)"
    
    def test_appointment_is_upcoming(self):
        """Test checking if appointment is upcoming."""
        apt = self.create_test_appointment()
        
        assert apt.is_upcoming() is True
        
        apt.cancel()
        assert apt.is_upcoming() is False


class TestLeadModel:
    """Tests for Lead data model."""
    
    def create_test_lead(self) -> Lead:
        """Create a test lead instance."""
        return Lead(
            id="LEAD-TEST001",
            contact_name="Jane Doe",
            contact_email="jane.doe@company.com",
            contact_phone="+44 9876 543210",
            company_name="ABC Transport Ltd",
            current_fleet_size=50,
            projected_fleet_size=75,
            timeline="1-3 months",
        )
    
    def test_lead_creation(self):
        """Test lead creation with required fields."""
        lead = self.create_test_lead()
        
        assert lead.id == "LEAD-TEST001"
        assert lead.contact_name == "Jane Doe"
        assert lead.status == LeadStatus.NEW
        assert lead.priority == LeadPriority.STANDARD
    
    def test_lead_score_calculation(self):
        """Test lead score calculation."""
        lead = self.create_test_lead()
        score = lead.calculate_score()
        
        # Should have points for: company name (10), fleet size 50+ (20), 
        # growth potential (10), timeline 1-3 months (20)
        assert score >= 50
        assert lead.priority in [LeadPriority.HIGH, LeadPriority.MEDIUM]
    
    def test_lead_score_high_priority(self):
        """Test that high-value leads get high priority."""
        lead = Lead(
            id="LEAD-HIGH001",
            contact_name="High Value",
            contact_email="high@value.com",
            contact_phone="+44 1111 111111",
            company_name="Big Corp",
            current_fleet_size=150,
            projected_fleet_size=200,
            timeline="Within 1 month",
            budget_range="£500k+",
            ev_interest=True,
        )
        score = lead.calculate_score()
        
        assert score >= 70
        assert lead.priority == LeadPriority.HIGH
    
    def test_lead_mark_contacted(self):
        """Test marking lead as contacted."""
        lead = self.create_test_lead()
        lead.mark_contacted("Called, left voicemail")
        
        assert lead.status == LeadStatus.CONTACTED
        assert lead.contacted_at is not None
        assert lead.follow_up_notes == "Called, left voicemail"
    
    def test_lead_qualify(self):
        """Test qualifying a lead."""
        lead = self.create_test_lead()
        lead.qualify("Interested in EV fleet")
        
        assert lead.status == LeadStatus.QUALIFIED
        assert lead.qualified_at is not None
    
    def test_lead_close_won(self):
        """Test closing lead as won."""
        lead = self.create_test_lead()
        lead.close_won()
        
        assert lead.status == LeadStatus.WON
        assert lead.closed_at is not None
    
    def test_lead_close_lost(self):
        """Test closing lead as lost."""
        lead = self.create_test_lead()
        lead.close_lost("Went with competitor")
        
        assert lead.status == LeadStatus.LOST
        assert lead.closed_at is not None
        assert "competitor" in lead.follow_up_notes.lower()
    
    def test_lead_to_dict(self):
        """Test converting lead to dictionary."""
        lead = self.create_test_lead()
        data = lead.to_dict()
        
        assert data["id"] == "LEAD-TEST001"
        assert data["contact_name"] == "Jane Doe"
        assert data["company_name"] == "ABC Transport Ltd"
        assert data["current_fleet_size"] == 50
    
    def test_lead_assign_to(self):
        """Test assigning lead to team member."""
        lead = self.create_test_lead()
        lead.assign_to("Sarah Jones")
        
        assert lead.assigned_to == "Sarah Jones"
        assert lead.updated_at is not None


class TestAppointmentTypes:
    """Tests for appointment type enums."""
    
    def test_all_appointment_types(self):
        """Test that all expected appointment types exist."""
        expected_types = ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo"]
        
        for type_name in expected_types:
            assert AppointmentType(type_name) is not None
    
    def test_all_time_slots(self):
        """Test that all expected time slots exist."""
        expected_slots = ["Morning (9-12)", "Afternoon (12-3)", "Late Afternoon (3-5)"]
        
        for slot in expected_slots:
            assert TimeSlot(slot) is not None


class TestLeadPriority:
    """Tests for lead priority calculations."""
    
    def test_priority_levels(self):
        """Test all priority levels exist."""
        assert LeadPriority.HIGH.value == "High"
        assert LeadPriority.MEDIUM.value == "Medium"
        assert LeadPriority.STANDARD.value == "Standard"
        assert LeadPriority.LOW.value == "Low"
    
    def test_contact_methods(self):
        """Test all contact methods exist."""
        assert ContactMethod.PHONE.value == "Phone"
        assert ContactMethod.EMAIL.value == "Email"
        assert ContactMethod.EITHER.value == "Either"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
