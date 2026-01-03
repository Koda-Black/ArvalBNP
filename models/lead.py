"""
Lead data models for Arval BNP Voice Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class LeadPriority(Enum):
    """Priority levels for leads based on scoring."""
    HIGH = "High"
    MEDIUM = "Medium"
    STANDARD = "Standard"
    LOW = "Low"


class LeadStatus(Enum):
    """Status of a lead in the sales pipeline."""
    NEW = "New"
    CONTACTED = "Contacted"
    QUALIFIED = "Qualified"
    PROPOSAL_SENT = "Proposal Sent"
    NEGOTIATION = "Negotiation"
    WON = "Won"
    LOST = "Lost"
    NURTURING = "Nurturing"


class ContactMethod(Enum):
    """Preferred contact method for leads."""
    PHONE = "Phone"
    EMAIL = "Email"
    EITHER = "Either"


class LeadSource(Enum):
    """Source of the lead."""
    VOICE_AGENT = "Voice Agent"
    WEBSITE = "Website"
    REFERRAL = "Referral"
    MARKETING = "Marketing Campaign"
    TRADE_SHOW = "Trade Show"
    COLD_CALL = "Cold Call"
    OTHER = "Other"


@dataclass
class Lead:
    """
    Represents a sales lead captured by the voice agent.
    """
    id: str
    contact_name: str
    contact_email: str
    contact_phone: str
    source: LeadSource = LeadSource.VOICE_AGENT
    status: LeadStatus = LeadStatus.NEW
    priority: LeadPriority = LeadPriority.STANDARD
    score: int = 0
    
    # Company information
    company_name: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    
    # Fleet information
    current_fleet_size: Optional[int] = None
    projected_fleet_size: Optional[int] = None
    current_provider: Optional[str] = None
    
    # Interests and requirements
    vehicle_interests: Optional[str] = None
    ev_interest: bool = False
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    specific_requirements: Optional[str] = None
    
    # Contact preferences
    preferred_contact_method: ContactMethod = ContactMethod.EITHER
    best_time_to_call: Optional[str] = None
    
    # Notes and history
    inquiry_notes: Optional[str] = None
    follow_up_notes: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    contacted_at: Optional[datetime] = None
    qualified_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # Assignment
    assigned_to: Optional[str] = None

    def calculate_score(self) -> int:
        """
        Calculate lead score based on various factors.
        Higher scores indicate more promising leads.
        """
        score = 0
        
        # Company information (10 points max)
        if self.company_name:
            score += 10
        
        # Fleet size scoring (35 points max)
        if self.current_fleet_size:
            if self.current_fleet_size >= 100:
                score += 25
            elif self.current_fleet_size >= 50:
                score += 20
            elif self.current_fleet_size >= 20:
                score += 15
            elif self.current_fleet_size >= 10:
                score += 10
            else:
                score += 5
        
        if self.projected_fleet_size and self.projected_fleet_size > (self.current_fleet_size or 0):
            score += 10  # Growth potential
        
        # Timeline scoring (25 points max)
        if self.timeline:
            timeline_lower = self.timeline.lower()
            if "immediate" in timeline_lower or "asap" in timeline_lower or "within 1 month" in timeline_lower:
                score += 25
            elif "1-3 month" in timeline_lower:
                score += 20
            elif "3-6 month" in timeline_lower:
                score += 15
            elif "6-12 month" in timeline_lower:
                score += 10
            else:
                score += 5
        
        # Budget indication (15 points max)
        if self.budget_range:
            score += 15
        
        # EV interest (10 points) - aligns with Arval sustainability focus
        if self.ev_interest:
            score += 10
        
        # Current provider (5 points) - switching potential
        if self.current_provider:
            score += 5
        
        self.score = score
        self._update_priority()
        return score

    def _update_priority(self) -> None:
        """Update priority based on current score."""
        if self.score >= 70:
            self.priority = LeadPriority.HIGH
        elif self.score >= 45:
            self.priority = LeadPriority.MEDIUM
        elif self.score >= 20:
            self.priority = LeadPriority.STANDARD
        else:
            self.priority = LeadPriority.LOW

    def to_dict(self) -> dict:
        """Convert lead to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "contact_name": self.contact_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "source": self.source.value,
            "status": self.status.value,
            "priority": self.priority.value,
            "score": self.score,
            "company_name": self.company_name,
            "company_size": self.company_size,
            "industry": self.industry,
            "current_fleet_size": self.current_fleet_size,
            "projected_fleet_size": self.projected_fleet_size,
            "current_provider": self.current_provider,
            "vehicle_interests": self.vehicle_interests,
            "ev_interest": self.ev_interest,
            "timeline": self.timeline,
            "budget_range": self.budget_range,
            "specific_requirements": self.specific_requirements,
            "preferred_contact_method": self.preferred_contact_method.value,
            "best_time_to_call": self.best_time_to_call,
            "inquiry_notes": self.inquiry_notes,
            "follow_up_notes": self.follow_up_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "contacted_at": self.contacted_at.isoformat() if self.contacted_at else None,
            "qualified_at": self.qualified_at.isoformat() if self.qualified_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "assigned_to": self.assigned_to,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Lead":
        """Create a Lead instance from a dictionary."""
        lead = cls(
            id=data["id"],
            contact_name=data["contact_name"],
            contact_email=data["contact_email"],
            contact_phone=data["contact_phone"],
            source=LeadSource(data.get("source", "Voice Agent")),
            status=LeadStatus(data.get("status", "New")),
            priority=LeadPriority(data.get("priority", "Standard")),
            score=data.get("score", 0),
            company_name=data.get("company_name"),
            company_size=data.get("company_size"),
            industry=data.get("industry"),
            current_fleet_size=data.get("current_fleet_size"),
            projected_fleet_size=data.get("projected_fleet_size"),
            current_provider=data.get("current_provider"),
            vehicle_interests=data.get("vehicle_interests"),
            ev_interest=data.get("ev_interest", False),
            timeline=data.get("timeline"),
            budget_range=data.get("budget_range"),
            specific_requirements=data.get("specific_requirements"),
            preferred_contact_method=ContactMethod(data.get("preferred_contact_method", "Either")),
            best_time_to_call=data.get("best_time_to_call"),
            inquiry_notes=data.get("inquiry_notes"),
            follow_up_notes=data.get("follow_up_notes"),
            assigned_to=data.get("assigned_to"),
        )
        
        # Parse timestamps
        if data.get("created_at"):
            lead.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            lead.updated_at = datetime.fromisoformat(data["updated_at"])
        if data.get("contacted_at"):
            lead.contacted_at = datetime.fromisoformat(data["contacted_at"])
        if data.get("qualified_at"):
            lead.qualified_at = datetime.fromisoformat(data["qualified_at"])
        if data.get("closed_at"):
            lead.closed_at = datetime.fromisoformat(data["closed_at"])
        
        return lead

    def mark_contacted(self, notes: Optional[str] = None) -> None:
        """Mark the lead as contacted."""
        self.status = LeadStatus.CONTACTED
        self.contacted_at = datetime.now()
        self.updated_at = datetime.now()
        if notes:
            self.follow_up_notes = notes

    def qualify(self, notes: Optional[str] = None) -> None:
        """Qualify the lead for further pursuit."""
        self.status = LeadStatus.QUALIFIED
        self.qualified_at = datetime.now()
        self.updated_at = datetime.now()
        if notes:
            self.follow_up_notes = notes

    def close_won(self) -> None:
        """Mark the lead as won (converted to customer)."""
        self.status = LeadStatus.WON
        self.closed_at = datetime.now()
        self.updated_at = datetime.now()

    def close_lost(self, reason: Optional[str] = None) -> None:
        """Mark the lead as lost."""
        self.status = LeadStatus.LOST
        self.closed_at = datetime.now()
        self.updated_at = datetime.now()
        if reason:
            self.follow_up_notes = f"Lost reason: {reason}"

    def assign_to(self, assignee: str) -> None:
        """Assign the lead to a team member."""
        self.assigned_to = assignee
        self.updated_at = datetime.now()

    def get_display_summary(self) -> str:
        """Get a human-readable summary of the lead."""
        company_info = f"\nCompany: {self.company_name}" if self.company_name else ""
        fleet_info = f"\nFleet Size: {self.current_fleet_size}" if self.current_fleet_size else ""
        
        return (
            f"Lead {self.id}\n"
            f"Name: {self.contact_name}\n"
            f"Email: {self.contact_email}\n"
            f"Phone: {self.contact_phone}"
            f"{company_info}"
            f"{fleet_info}\n"
            f"Priority: {self.priority.value}\n"
            f"Score: {self.score}\n"
            f"Status: {self.status.value}"
        )
