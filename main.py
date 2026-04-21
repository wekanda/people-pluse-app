from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from database import engine, Base, get_db
from routers import employees, leave, timesheet, appraisal, documents, notifications, upload
from auth_router import router as auth_router
import models
import sys

print("Starting People Pluse API...", file=sys.stderr)

try:
    print("Creating database tables...", file=sys.stderr)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully", file=sys.stderr)
except Exception as e:
    print(f"Error creating database tables: {e}", file=sys.stderr)

# Ensure new SQLite columns exist when the app schema evolves.
def ensure_schema_columns():
    db_url = str(engine.url)
    if "sqlite" in db_url:
        try:
            with engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(employees)"))
                columns = [row[1] for row in result]
                if 'location' not in columns:
                    conn.execute(text('ALTER TABLE employees ADD COLUMN location VARCHAR'))
                    conn.commit()
        except Exception as e:
            print(f"SQLite schema check warning: {e}", file=sys.stderr)

try:
    ensure_schema_columns()
except Exception as e:
    print(f"Schema initialization warning: {e}", file=sys.stderr)

app = FastAPI(title="PEOPLE PLUSE API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(employees.router)
app.include_router(leave.router)
app.include_router(timesheet.router)
app.include_router(appraisal.router)
app.include_router(documents.router)
app.include_router(notifications.router)
app.include_router(upload.router)

@app.get("/api/health")
def root():
    return {"message": "PEOPLE PLUSE API running"}

@app.get("/api/debug/users")
def debug_users(db: Session = Depends(get_db)):
    """Debug endpoint to check users"""
    users = db.query(models.User).all()
    return {
        "users": [{"id": u.id, "email": u.email, "role": u.role} for u in users],
        "count": len(users)
    }

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    total_staff = db.query(models.Employee).count()
    active_staff = db.query(models.Employee).filter(models.Employee.status == "Active").count()
    
    # Contracts expiring in next 30 days
    today = datetime.now().date()
    thirty_days_later = today + timedelta(days=30)
    expiring_soon = db.query(models.Employee).filter(
        models.Employee.contract_end.between(today, thirty_days_later)
    ).count()
    
    # Missing documents
    missing_docs = db.query(models.Employee).filter(
        (models.Employee.missing_app_resume == True) |
        (models.Employee.missing_national_id == True) |
        (models.Employee.missing_appointment_letter == True)
    ).count()

    project_count = db.query(models.Employee.project).distinct().count()
    location_count = db.query(models.Employee.location).filter(models.Employee.location != None).distinct().count()
    
    # Get list of expiring contracts
    expiring_contracts = db.query(models.Employee).filter(
        models.Employee.contract_end.between(today, thirty_days_later)
    ).all()
    
    expiring_list = [
        {
            "full_name": emp.full_name,
            "file_code": emp.file_code,
            "contract_end": str(emp.contract_end),
            "project": emp.project
        }
        for emp in expiring_contracts
    ]
    
    return {
        "total_staff": total_staff,
        "active_staff": active_staff,
        "contracts_expiring_soon": expiring_soon,
        "staff_with_missing_docs": missing_docs,
        "project_count": project_count,
        "location_count": location_count,
        "expiring_contracts": expiring_list
    }

# Mount static files LAST so API routes take precedence
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}", file=sys.stderr)
