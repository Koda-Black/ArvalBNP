"""
Arval BNP Paribas Voice Agent Tools
Function tools for appointment booking, lead capture, and customer support.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Optional
from zoneinfo import ZoneInfo

# UK timezone
UK_TZ = ZoneInfo("Europe/London")

# Data storage paths
DATA_DIR = Path(__file__).parent.parent / "data"
APPOINTMENTS_FILE = DATA_DIR / "appointments.json"
LEADS_FILE = DATA_DIR / "leads.json"
CALLBACKS_FILE = DATA_DIR / "callbacks.json"


def _ensure_data_dir():
    """Ensure the data directory exists."""
    DATA_DIR.mkdir(exist_ok=True)


def _load_json(file_path: Path) -> list:
    """Load JSON data from file."""
    if file_path.exists():
        with open(file_path, "r") as f:
            return json.load(f)
    return []


def _save_json(file_path: Path, data: list):
    """Save JSON data to file."""
    _ensure_data_dir()
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def book_appointment(
    customer_name: Annotated[str, "The full name of the customer"],
    contact_phone: Annotated[str, "Customer's phone number for appointment confirmation"],
    contact_email: Annotated[str, "Customer's email address"],
    appointment_type: Annotated[str, "Type of appointment: 'MOT', 'Service', 'Inspection', 'Fleet Consultation', or 'Sales Demo'"],
    preferred_date: Annotated[str, "Preferred date for the appointment in YYYY-MM-DD format"],
    preferred_time: Annotated[str, "Preferred time slot: 'Morning (9-12)', 'Afternoon (12-3)', or 'Late Afternoon (3-5)'"],
    vehicle_registration: Annotated[Optional[str], "Vehicle registration number (if applicable)"] = None,
    additional_notes: Annotated[Optional[str], "Any additional notes or special requirements"] = None,
) -> str:
    """
    Book an appointment for a customer. Use this tool when a customer wants to schedule
    an MOT, service appointment, vehicle inspection, fleet consultation, or sales demo.
    """
    # Validate appointment type
    valid_types = ["MOT", "Service", "Inspection", "Fleet Consultation", "Sales Demo"]
    if appointment_type not in valid_types:
        return f"Invalid appointment type. Please choose from: {', '.join(valid_types)}"
    
    # Validate and parse date
    try:
        appointment_date = datetime.strptime(preferred_date, "%Y-%m-%d")
        
        # Check if date is in the past
        today = datetime.now(UK_TZ).date()
        if appointment_date.date() < today:
            return "Cannot book appointments in the past. Please provide a future date."
        
        # Check if date is a weekend
        if appointment_date.weekday() >= 5:
            return "We're closed on weekends. Please choose a Monday to Friday date."
            
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2026-01-15)."
    
    # Create appointment record
    appointment = {
        "id": f"APT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_name": customer_name,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "type": appointment_type,
        "date": preferred_date,
        "time_slot": preferred_time,
        "vehicle_registration": vehicle_registration,
        "notes": additional_notes,
        "status": "Confirmed",
        "created_at": datetime.now(UK_TZ).isoformat(),
    }
    
    # Save appointment
    appointments = _load_json(APPOINTMENTS_FILE)
    appointments.append(appointment)
    _save_json(APPOINTMENTS_FILE, appointments)
    
    return f"""✅ Appointment Successfully Booked!

**Appointment Details:**
- Reference: {appointment['id']}
- Type: {appointment_type}
- Date: {preferred_date}
- Time: {preferred_time}
- Customer: {customer_name}

A confirmation email will be sent to {contact_email}.
If you need to reschedule, please call us or reference your booking ID: {appointment['id']}

Is there anything else I can help you with?"""


def capture_lead(
    contact_name: Annotated[str, "Full name of the prospective customer"],
    contact_email: Annotated[str, "Email address for follow-up"],
    contact_phone: Annotated[str, "Phone number for follow-up"],
    company_name: Annotated[Optional[str], "Company name (for business inquiries)"] = None,
    current_fleet_size: Annotated[Optional[int], "Current number of vehicles in fleet"] = None,
    projected_fleet_size: Annotated[Optional[int], "Projected fleet size after leasing"] = None,
    current_provider: Annotated[Optional[str], "Current leasing provider, if any"] = None,
    vehicle_interests: Annotated[Optional[str], "Specific vehicle types or models of interest"] = None,
    timeline: Annotated[Optional[str], "Decision timeline (e.g., 'Within 1 month', '3-6 months')"] = None,
    budget_range: Annotated[Optional[str], "Budget considerations or range"] = None,
    preferred_contact_method: Annotated[str, "Preferred method: 'Phone', 'Email', or 'Either'"] = "Either",
    inquiry_notes: Annotated[Optional[str], "Additional notes about the inquiry"] = None,
) -> str:
    """
    Capture lead information from a prospective customer interested in fleet leasing
    or vehicle services. Use this tool when someone expresses interest in Arval services.
    """
    # Create lead record
    lead = {
        "id": f"LEAD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "contact_name": contact_name,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "company_name": company_name,
        "current_fleet_size": current_fleet_size,
        "projected_fleet_size": projected_fleet_size,
        "current_provider": current_provider,
        "vehicle_interests": vehicle_interests,
        "timeline": timeline,
        "budget_range": budget_range,
        "preferred_contact_method": preferred_contact_method,
        "inquiry_notes": inquiry_notes,
        "status": "New",
        "source": "Voice Agent",
        "created_at": datetime.now(UK_TZ).isoformat(),
    }
    
    # Calculate lead score (simple scoring)
    score = 0
    if company_name:
        score += 10
    if current_fleet_size and current_fleet_size > 10:
        score += 20
    if projected_fleet_size and projected_fleet_size > 20:
        score += 15
    if timeline in ["Within 1 month", "1-3 months"]:
        score += 25
    if budget_range:
        score += 10
    
    lead["score"] = score
    lead["priority"] = "High" if score >= 50 else "Medium" if score >= 25 else "Standard"
    
    # Save lead
    leads = _load_json(LEADS_FILE)
    leads.append(lead)
    _save_json(LEADS_FILE, leads)
    
    return f"""✅ Thank you for your interest in Arval!

I've captured your details and our fleet solutions team will be in touch shortly.

**Your Reference:** {lead['id']}
**Preferred Contact:** {preferred_contact_method}

Our team typically responds within 1 business day. In the meantime, is there anything else I can help you with or any other questions about our services?"""


def get_business_hours() -> str:
    """
    Get the current business hours for Arval Driver Desk.
    Use this when a customer asks about operating hours.
    """
    return """**Arval Driver Desk Business Hours:**

🕘 **Standard Hours:** Monday to Friday, 9:00 AM - 5:00 PM GMT

**Part-Time Support Available:**
- Morning Shift: 9:00 AM - 1:00 PM
- Afternoon Shift: 10:00 AM - 2:00 PM

**24/7 Services:**
🚗 Emergency Roadside Assistance is available around the clock.

**Location:** Swindon, Wiltshire, UK

**Note:** We're closed on weekends and UK bank holidays. For urgent matters outside business hours, please contact our 24/7 roadside assistance line."""


def check_after_hours() -> str:
    """
    Check if it's currently after business hours and provide appropriate guidance.
    Use this tool to determine if the caller is reaching out during or outside business hours.
    """
    now = datetime.now(UK_TZ)
    current_hour = now.hour
    current_weekday = now.weekday()  # 0 = Monday, 6 = Sunday
    
    is_weekend = current_weekday >= 5
    is_before_hours = current_hour < 9
    is_after_hours = current_hour >= 17
    
    if is_weekend:
        next_monday = now + timedelta(days=(7 - current_weekday))
        return f"""🌙 **After Hours Notice**

You're calling during the weekend. Our Driver Desk reopens on Monday at 9:00 AM GMT.

**What I can help with now:**
- Answer frequently asked questions
- Capture your inquiry for priority callback on Monday
- Provide 24/7 emergency roadside assistance contact

**Next Business Day:** {next_monday.strftime('%A, %B %d, %Y')}

Would you like me to schedule a callback for Monday, or is this an emergency requiring roadside assistance?"""
    
    elif is_before_hours or is_after_hours:
        time_status = "before" if is_before_hours else "after"
        next_open = "9:00 AM today" if is_before_hours else "9:00 AM tomorrow"
        
        if current_weekday == 4 and is_after_hours:  # Friday after hours
            next_open = "9:00 AM on Monday"
        
        return f"""🌙 **After Hours Notice**

You're calling {time_status} our regular business hours. We'll be open again at {next_open}.

**What I can help with now:**
- Answer frequently asked questions
- Capture your inquiry for priority callback
- Provide 24/7 emergency roadside assistance contact

Would you like me to schedule a callback, or is there something urgent I can help with?"""
    
    else:
        return f"""✅ **Within Business Hours**

Great news! You're calling during our regular business hours.
Current time: {now.strftime('%I:%M %p GMT on %A, %B %d')}

I'm fully available to assist you with any inquiries, appointments, or services. How can I help you today?"""


def get_roadside_assistance() -> str:
    """
    Provide emergency roadside assistance information.
    Use this when a customer has a breakdown or emergency vehicle situation.
    """
    return """🚨 **Arval Emergency Roadside Assistance**

Our 24/7 roadside assistance service is here to help!

**For Immediate Assistance:**
📞 Contact our dedicated roadside assistance provider directly.
Our team can connect you right away.

**What to have ready:**
- Your vehicle registration number
- Your exact location (postcode if possible)
- Description of the issue
- Your contact phone number

**Services Available:**
✅ Breakdown recovery
✅ Battery jump-start
✅ Flat tire assistance
✅ Fuel delivery
✅ Lockout service
✅ Towing if needed

**Safety First:**
If you're on a motorway or in an unsafe location, please ensure your own safety first. Turn on hazard lights and move to a safe location if possible.

Shall I connect you with roadside assistance now, or is there other information you need?"""


def schedule_callback(
    customer_name: Annotated[str, "The customer's full name"],
    contact_phone: Annotated[str, "Phone number to call back"],
    preferred_time: Annotated[str, "Preferred callback time: 'Morning', 'Afternoon', 'ASAP', or specific time"],
    callback_reason: Annotated[str, "Brief description of what the callback is regarding"],
    is_urgent: Annotated[bool, "Whether this is an urgent matter requiring priority callback"] = False,
) -> str:
    """
    Schedule a callback request for the customer.
    Use this when a customer wants to be called back during business hours.
    """
    now = datetime.now(UK_TZ)
    
    # Determine next business day if after hours
    next_business_day = now
    if now.weekday() >= 5:  # Weekend
        days_until_monday = 7 - now.weekday()
        next_business_day = now + timedelta(days=days_until_monday)
    elif now.hour >= 17:  # After 5 PM
        if now.weekday() == 4:  # Friday
            next_business_day = now + timedelta(days=3)
        else:
            next_business_day = now + timedelta(days=1)
    
    callback = {
        "id": f"CB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "customer_name": customer_name,
        "contact_phone": contact_phone,
        "preferred_time": preferred_time,
        "reason": callback_reason,
        "is_urgent": is_urgent,
        "status": "Pending",
        "scheduled_date": next_business_day.strftime("%Y-%m-%d"),
        "created_at": now.isoformat(),
    }
    
    # Save callback request
    callbacks = _load_json(CALLBACKS_FILE)
    callbacks.append(callback)
    _save_json(CALLBACKS_FILE, callbacks)
    
    priority_text = "🔴 PRIORITY" if is_urgent else "📞"
    
    return f"""{priority_text} **Callback Scheduled!**

**Reference:** {callback['id']}
**For:** {customer_name}
**Phone:** {contact_phone}
**Preferred Time:** {preferred_time}
**Scheduled For:** {next_business_day.strftime('%A, %B %d, %Y')}

Our team will call you back during your preferred time slot. {'This has been marked as urgent and will be prioritized.' if is_urgent else ''}

Is there anything else I can help you with in the meantime?"""


def get_faq_answer(
    topic: Annotated[str, "The topic of the FAQ question: 'leasing', 'fleet', 'ev', 'mot', 'pricing', 'contracts', 'careers', 'general'"],
) -> str:
    """
    Get answers to frequently asked questions about Arval services.
    Use this to provide quick answers to common questions.
    """
    faqs = {
        "leasing": """**Vehicle Leasing FAQs:**

**Q: What is full-service vehicle leasing?**
A: Full-service leasing includes the vehicle, maintenance, insurance, road tax, and breakdown cover in one monthly payment. No hidden costs!

**Q: How long are typical lease terms?**
A: Lease terms typically range from 24 to 48 months, depending on your needs. We offer flexible options for businesses of all sizes.

**Q: Can I lease electric vehicles?**
A: Absolutely! We're committed to sustainability and offer a wide range of EVs. We can help you transition your entire fleet to electric.

**Q: What happens at the end of the lease?**
A: You simply return the vehicle, and we handle everything else. You can also choose to extend or upgrade to a new vehicle.""",

        "fleet": """**Fleet Management FAQs:**

**Q: What fleet sizes do you work with?**
A: We work with fleets of all sizes - from small businesses with a few vehicles to large corporations with thousands.

**Q: What's included in fleet management?**
A: Our services include vehicle sourcing, maintenance scheduling, fuel management, driver support, reporting, and end-of-life management.

**Q: How many vehicles does Arval manage?**
A: We manage over 190,000 vehicles in the UK and 1.82 million globally across 28 countries.

**Q: Can you help us go electric?**
A: Yes! We specialize in helping companies transition to electric vehicles with our EV expertise and charging solutions.""",

        "ev": """**Electric Vehicle FAQs:**

**Q: Does Arval offer electric vehicles?**
A: Yes! We're passionate about sustainability and offer a comprehensive range of EVs from all major manufacturers.

**Q: Do you provide charging solutions?**
A: We can help arrange charging infrastructure for your business and advise on home charging for drivers.

**Q: What support is available for EV drivers?**
A: Our Driver Desk provides full support for EV drivers, including charging network assistance and EV-specific guidance.

**Q: Are EVs more expensive to lease?**
A: While some EVs have higher monthly costs, total cost of ownership is often lower due to reduced fuel and maintenance costs.""",

        "mot": """**MOT & Service FAQs:**

**Q: How do I book an MOT?**
A: Simply call our Driver Desk or use this voice service! We'll arrange everything for you.

**Q: Is MOT included in my lease?**
A: Yes, MOT is typically included in our full-service lease packages.

**Q: What if my vehicle fails its MOT?**
A: Don't worry - we handle any required repairs. You'll receive a courtesy vehicle if needed.

**Q: How much notice do I need to give?**
A: We recommend booking at least 2 weeks in advance, but we can often accommodate shorter notice.""",

        "pricing": """**Pricing & Costs FAQs:**

**Q: How is the monthly payment calculated?**
A: Monthly payments are based on the vehicle value, lease term, expected mileage, and included services.

**Q: Are there any hidden costs?**
A: Our full-service lease includes everything - no hidden costs. What you see is what you pay.

**Q: Can I change my mileage allowance?**
A: Yes, mileage can often be adjusted during the lease. Speak to your account manager for options.

**Q: What payment methods do you accept?**
A: We accept direct debit for monthly payments. Speak to our finance team for detailed options.""",

        "contracts": """**Contract FAQs:**

**Q: What's the minimum lease term?**
A: Minimum terms are typically 24 months, but we offer flexible options based on your needs.

**Q: Can I end my lease early?**
A: Early termination may be possible with an early termination fee. Contact your account manager to discuss options.

**Q: What happens if I exceed my mileage?**
A: Excess mileage is charged at a per-mile rate agreed at the start of your lease.

**Q: Is there a cooling-off period?**
A: Business leases don't have a statutory cooling-off period, but please discuss concerns with us before signing.""",

        "careers": """**Careers at Arval FAQs:**

**Q: What roles are available?**
A: We have opportunities in customer service, fleet management, sales, finance, and more. Visit our careers page for current openings.

**Q: Is training provided?**
A: Yes! New employees receive a comprehensive 5-week training programme before taking on full responsibilities.

**Q: What's the work culture like?**
A: We're more human than corporate - friendly, supportive, and focused on great customer outcomes.

**Q: Do you offer hybrid working?**
A: Yes, we offer hybrid working from our Swindon office once you're settled in the role.""",

        "general": """**General FAQs:**

**Q: Who is Arval?**
A: Arval is a global leader in vehicle leasing, part of BNP Paribas Group. We manage over 1.82 million vehicles across 28 countries.

**Q: Where are you based?**
A: Our UK headquarters is in Swindon, Wiltshire. We operate across 28 countries globally.

**Q: How can I contact you?**
A: Call our Driver Desk (Mon-Fri, 9AM-5PM GMT), email, or chat with this voice agent 24/7!

**Q: What makes Arval different?**
A: Our focus on Service, Sustainability, and Solutions - plus our friendly, no-script approach to customer care.""",
    }
    
    if topic.lower() in faqs:
        return faqs[topic.lower()]
    else:
        topics_list = ", ".join(faqs.keys())
        return f"I have FAQs available for these topics: {topics_list}. Which topic would you like to know more about?"
