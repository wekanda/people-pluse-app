#!/usr/bin/env python3
"""
Seed script to populate the database with test data
Run this after starting the backend for the first time
"""

from database import SessionLocal, engine
from models import Base, User, Employee
from auth import get_password_hash, verify_password
from datetime import date, timedelta

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
test_users = [
    {
        "email": "admin@peoplepluse.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "hr_admin"
    },
    {
        "email": "manager@peoplepluse.com",
        "password": "manager123",
        "full_name": "Project Manager",
        "role": "project_manager"
    },
    {
        "email": "staff@peoplepluse.com",
        "password": "staff123",
        "full_name": "Staff Member",
        "role": "staff"
    }
]

# Add users if they don't exist or repair them if the stored password is stale
for user_data in test_users:
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    if existing:
        try:
            if not verify_password(user_data["password"], existing.hashed_password):
                existing.hashed_password = get_password_hash(user_data["password"])
                existing.full_name = user_data["full_name"]
                existing.role = user_data["role"]
                db.add(existing)
                print(f"Updated password for existing user: {user_data['email']}")
        except Exception:
            existing.hashed_password = get_password_hash(user_data["password"])
            existing.full_name = user_data["full_name"]
            existing.role = user_data["role"]
            db.add(existing)
            print(f"Repaired corrupted user record: {user_data['email']}")
    else:
        hashed_pass = get_password_hash(user_data["password"])
        user = User(
            email=user_data["email"],
            hashed_password=hashed_pass,
            full_name=user_data["full_name"],
            role=user_data["role"]
        )
        db.add(user)
        print(f"Created user: {user_data['email']}")

# Create test employees
test_employees = [
    {
        "file_code": "TPO/001",
        "full_name": "John Kamau",
        "project": "HEAD OFFICE",
        "status": "Active",
        "position": "HR Manager",
        "contact_number": "0700000001",
        "locker": "HEAD OFFICE",
        "date_of_appointment": date(2020, 1, 15),
        "contract_start": date(2023, 1, 1),
        "contract_end": date(2025, 12, 31),
        "employment_type": "Fixed",
        "notice_period": "1 Month"
    },
    {
        "file_code": "TPO/002",
        "full_name": "Jane Mwangi",
        "project": "USAID-KCHS",
        "status": "Active",
        "position": "Project Coordinator",
        "contact_number": "0700000002",
        "locker": "USAID-KCHS",
        "date_of_appointment": date(2021, 3, 10),
        "contract_start": date(2023, 6, 1),
        "contract_end": date(2024, 5, 31),
        "employment_type": "Short Term",
        "notice_period": "2 Weeks"
    },
    {
        "file_code": "TPO/003",
        "full_name": "Peter Otieno",
        "project": "DCA-ADI",
        "status": "Active",
        "position": "Finance Officer",
        "contact_number": "0700000003",
        "locker": "DCA-ADI",
        "date_of_appointment": date(2019, 6, 20),
        "contract_start": date(2022, 1, 1),
        "contract_end": date(2025, 6, 30),
        "employment_type": "Fixed",
        "notice_period": "1 Month"
    },
    {
        "file_code": "TPO/004",
        "full_name": "Grace Kipchoge",
        "project": "UNHCR",
        "status": "Active",
        "position": "Operations Officer",
        "contact_number": "0700000004",
        "locker": "UNHCR",
        "date_of_appointment": date(2022, 2, 1),
        "contract_start": date(2024, 1, 1),
        "contract_end": date(2024, 12, 31),
        "employment_type": "Fixed",
        "notice_period": "1 Month",
        "missing_app_resume": True,
        "missing_national_id": True
    }
]

# Add employees if they don't exist
for emp_data in test_employees:
    existing = db.query(Employee).filter(Employee.file_code == emp_data["file_code"]).first()
    if not existing:
        employee = Employee(**emp_data)
        db.add(employee)
        print(f"Created employee: {emp_data['full_name']} ({emp_data['file_code']})")

db.commit()
db.close()

print("\n✅ Database seeded successfully!")
print("\nTest credentials:")
for user in test_users:
    print(f"  Email: {user['email']}, Password: {user['password']}")
