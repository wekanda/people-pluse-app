"""
Database seed script to initialize required data for HR system
Run this after applying database migrations
"""
from database import SessionLocal
import models
from datetime import datetime

def seed_database():
    """Initialize database with required leave types and document types."""
    db = SessionLocal()
    
    try:
        # Create all tables first
        models.Base.metadata.create_all(bind=db.get_bind())
        
        # Check if data already exists
        leave_count = db.query(models.LeaveType).count()
        doc_count = db.query(models.DocumentType).count()
        
        if leave_count == 0:
            print("Seeding leave types...")
            
            leave_types = [
                {
                    "name": "Annual Leave",
                    "annual_entitlement_days": 21.0,
                    "description": "Minimum 21 working days after 12-15 months of service",
                    "is_paid": True,
                    "requires_manager_approval": True
                },
                {
                    "name": "Sick Leave",
                    "annual_entitlement_days": 60.0,
                    "description": "Up to 2 months per year. First month paid, subsequent unpaid",
                    "is_paid": True,
                    "requires_manager_approval": False
                },
                {
                    "name": "Maternity Leave",
                    "annual_entitlement_days": 60.0,
                    "description": "60 working days fully paid for female employees",
                    "is_paid": True,
                    "requires_manager_approval": True
                },
                {
                    "name": "Paternity Leave",
                    "annual_entitlement_days": 4.0,
                    "description": "4 working days fully paid for fathers",
                    "is_paid": True,
                    "requires_manager_approval": True
                },
                {
                    "name": "Compassionate Leave",
                    "annual_entitlement_days": 5.0,
                    "description": "Granted for bereavement or family emergencies",
                    "is_paid": True,
                    "requires_manager_approval": True
                },
                {
                    "name": "Study Leave",
                    "annual_entitlement_days": 0.0,
                    "description": "Variable per policy - unpaid or partially paid",
                    "is_paid": False,
                    "requires_manager_approval": True
                },
                {
                    "name": "Adoption Leave",
                    "annual_entitlement_days": 0.0,
                    "description": "Variable per policy - granted voluntarily",
                    "is_paid": False,
                    "requires_manager_approval": True
                },
                {
                    "name": "Public Holidays",
                    "annual_entitlement_days": 14.0,
                    "description": "14+ paid days off annually",
                    "is_paid": True,
                    "requires_manager_approval": False
                }
            ]
            
            for lt in leave_types:
                leave_type = models.LeaveType(**lt)
                db.add(leave_type)
            
            db.commit()
            print(f"✓ Created {len(leave_types)} leave types")
        
        if doc_count == 0:
            print("Seeding document types...")
            
            document_types = [
                # PCM Department uploads
                {"name": "Employment Contract", "category": "pcm", "is_required": True, "expiry_period_days": None},
                {"name": "Job Description", "category": "pcm", "is_required": True, "expiry_period_days": None},
                {"name": "Appointment Letter", "category": "pcm", "is_required": True, "expiry_period_days": None},
                {"name": "National ID Copy", "category": "pcm", "is_required": True, "expiry_period_days": None},
                {"name": "Academic Certificates", "category": "pcm", "is_required": True, "expiry_period_days": None},
                {"name": "Professional Certificates", "category": "pcm", "is_required": False, "expiry_period_days": 365},
                {"name": "Reference Check Report", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Performance Appraisal", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Disciplinary Records", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Promotion Letter", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Salary Review Letter", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Exit Clearance Documents", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Training Certificates", "category": "pcm", "is_required": False, "expiry_period_days": None},
                {"name": "Medical Insurance Records", "category": "pcm", "is_required": False, "expiry_period_days": 365},
                
                # Manager uploads
                {"name": "Performance Appraisal Form", "category": "manager", "is_required": False, "expiry_period_days": None},
                {"name": "Probation Assessment", "category": "manager", "is_required": False, "expiry_period_days": None},
                {"name": "Training Recommendations", "category": "manager", "is_required": False, "expiry_period_days": None},
                {"name": "Leave Recommendations", "category": "manager", "is_required": False, "expiry_period_days": None},
                {"name": "Departmental Reports", "category": "manager", "is_required": False, "expiry_period_days": None},
                
                # Staff uploads
                {"name": "Updated CV", "category": "staff", "is_required": False, "expiry_period_days": None},
                {"name": "Staff Photograph", "category": "staff", "is_required": True, "expiry_period_days": None},
                {"name": "Passport Photograph", "category": "staff", "is_required": False, "expiry_period_days": None},
                {"name": "Bank Account Details", "category": "staff", "is_required": True, "expiry_period_days": None},
                {"name": "Tax Documents (TIN)", "category": "staff", "is_required": True, "expiry_period_days": None},
                {"name": "Medical Insurance Documents", "category": "staff", "is_required": False, "expiry_period_days": 365},
                {"name": "Leave Supporting Documents", "category": "staff", "is_required": False, "expiry_period_days": None},
                {"name": "Training Completion Certificates", "category": "staff", "is_required": False, "expiry_period_days": None},
            ]
            
            for dt in document_types:
                doc_type = models.DocumentType(**dt)
                db.add(doc_type)
            
            db.commit()
            print(f"✓ Created {len(document_types)} document types")
        
        # Create company settings if not exists
        settings_count = db.query(models.CompanySettings).count()
        if settings_count == 0:
            print("Creating company settings...")
            settings = models.CompanySettings(
                company_name="People Plus Uganda",
                contact_email="info@peoplepluse.com",
                contact_phone="+256-700-000000",
                address="Kampala, Uganda",
                country="Uganda"
            )
            db.add(settings)
            db.commit()
            print("✓ Created company settings")
        
        print("\n✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
