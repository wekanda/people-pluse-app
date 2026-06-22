"""
Seed script for Phase 1: Initialize leave types and document types
per Ugandan labor standards
"""

from database import SessionLocal, engine
import models
from datetime import datetime

def seed_leave_types():
    """Create standard leave types per Uganda Employment Act."""
    db = SessionLocal()
    
    leave_types = [
        {
            "name": "Annual Leave",
            "annual_entitlement_days": 21,  # Uganda: minimum 21 days/year
            "description": "Paid annual leave (21 working days minimum)",
            "is_paid": True,
            "requires_manager_approval": True
        },
        {
            "name": "Sick Leave",
            "annual_entitlement_days": 60,  # Uganda: 2 months/year
            "description": "Paid sick leave (2 months per year)",
            "is_paid": True,
            "requires_manager_approval": False
        },
        {
            "name": "Maternity Leave",
            "annual_entitlement_days": 60,  # Uganda: 60 days
            "description": "Paid maternity leave (60 days)",
            "is_paid": True,
            "requires_manager_approval": False
        },
        {
            "name": "Paternity Leave",
            "annual_entitlement_days": 4,  # Uganda: 4 days
            "description": "Paid paternity leave (4 days)",
            "is_paid": True,
            "requires_manager_approval": False
        },
        {
            "name": "Compassionate Leave",
            "annual_entitlement_days": 3,
            "description": "Leave for family emergencies or death",
            "is_paid": True,
            "requires_manager_approval": True
        },
        {
            "name": "Study Leave",
            "annual_entitlement_days": 5,
            "description": "Leave for professional development/exams",
            "is_paid": True,
            "requires_manager_approval": True
        },
        {
            "name": "Adoption Leave",
            "annual_entitlement_days": 30,
            "description": "Leave for adoption of children",
            "is_paid": True,
            "requires_manager_approval": False
        },
        {
            "name": "Public Holiday",
            "annual_entitlement_days": 13,
            "description": "Ugandan public holidays (paid)",
            "is_paid": True,
            "requires_manager_approval": False
        }
    ]
    
    for lt in leave_types:
        existing = db.query(models.LeaveType).filter(
            models.LeaveType.name == lt["name"]
        ).first()
        
        if not existing:
            db_leave_type = models.LeaveType(**lt)
            db.add(db_leave_type)
            print(f"✓ Created leave type: {lt['name']}")
        else:
            print(f"✓ Leave type already exists: {lt['name']}")
    
    db.commit()
    db.close()


def seed_document_types():
    """Create standard document types for e-PFile."""
    db = SessionLocal()
    
    document_types = [
        # Personal
        {
            "name": "National Identification",
            "category": "personal",
            "is_required": True,
            "expiry_period_days": 365 * 10  # 10 years
        },
        {
            "name": "Passport",
            "category": "personal",
            "is_required": False,
            "expiry_period_days": 365 * 10
        },
        # Employment
        {
            "name": "Employment Contract",
            "category": "employment",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Appointment Letter",
            "category": "employment",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Job Offer Letter",
            "category": "employment",
            "is_required": False,
            "expiry_period_days": None
        },
        # Qualifications
        {
            "name": "Academic Certificates",
            "category": "qualification",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Professional Qualifications",
            "category": "qualification",
            "is_required": False,
            "expiry_period_days": None
        },
        {
            "name": "Professional License",
            "category": "qualification",
            "is_required": False,
            "expiry_period_days": 365 * 5  # Typical renewal period
        },
        # Medical
        {
            "name": "Medical Clearance",
            "category": "medical",
            "is_required": False,
            "expiry_period_days": 365  # Annual renewal
        },
        {
            "name": "Medical Insurance",
            "category": "medical",
            "is_required": False,
            "expiry_period_days": 365
        },
        # Compliance
        {
            "name": "Tax Identification Number",
            "category": "compliance",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Bank Details",
            "category": "compliance",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Emergency Contact Form",
            "category": "compliance",
            "is_required": True,
            "expiry_period_days": 365 * 2
        },
        {
            "name": "Confidentiality Agreement",
            "category": "compliance",
            "is_required": True,
            "expiry_period_days": None
        },
        {
            "name": "Code of Conduct Acknowledgment",
            "category": "compliance",
            "is_required": True,
            "expiry_period_days": 365
        },
        # Performance
        {
            "name": "Performance Appraisal",
            "category": "performance",
            "is_required": False,
            "expiry_period_days": 365
        },
        {
            "name": "Training Records",
            "category": "performance",
            "is_required": False,
            "expiry_period_days": None
        },
        # Administrative
        {
            "name": "Termination Letter",
            "category": "administrative",
            "is_required": False,
            "expiry_period_days": None
        },
        {
            "name": "Exit Clearance",
            "category": "administrative",
            "is_required": False,
            "expiry_period_days": None
        },
    ]
    
    for dt in document_types:
        existing = db.query(models.DocumentType).filter(
            models.DocumentType.name == dt["name"]
        ).first()
        
        if not existing:
            db_doc_type = models.DocumentType(**dt)
            db.add(db_doc_type)
            print(f"✓ Created document type: {dt['name']}")
        else:
            print(f"✓ Document type already exists: {dt['name']}")
    
    db.commit()
    db.close()


def init_leave_balances():
    """Initialize leave balances for all employees."""
    db = SessionLocal()
    
    employees = db.query(models.Employee).all()
    leave_types = db.query(models.LeaveType).all()
    
    for employee in employees:
        for leave_type in leave_types:
            existing = db.query(models.LeaveBalance).filter(
                models.LeaveBalance.employee_id == employee.id,
                models.LeaveBalance.leave_type_id == leave_type.id
            ).first()
            
            if not existing:
                balance = models.LeaveBalance(
                    employee_id=employee.id,
                    leave_type_id=leave_type.id,
                    balance=leave_type.annual_entitlement_days,
                    accrued=leave_type.annual_entitlement_days,
                    used=0,
                    last_updated=datetime.utcnow()
                )
                db.add(balance)
    
    db.commit()
    count = db.query(models.LeaveBalance).count()
    print(f"✓ Total leave balances initialized: {count}")
    db.close()


if __name__ == "__main__":
    # Create all tables
    models.Base.metadata.create_all(bind=engine)
    print("✓ Database tables created/verified")
    
    # Seed data
    print("\n=== Seeding Leave Types ===")
    seed_leave_types()
    
    print("\n=== Seeding Document Types ===")
    seed_document_types()
    
    print("\n=== Initializing Leave Balances ===")
    init_leave_balances()
    
    print("\n✓ Phase 1 seeding complete!")
