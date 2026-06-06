from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, date, timedelta
from database import engine, Base, get_db
from routers import employees, leave, timesheet, appraisal, documents, notifications, upload
from auth_router import router as auth_router
from auth import get_current_user
import models

Base.metadata.create_all(bind=engine)

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
                if 'photo_url' not in columns:
                    conn.execute(text('ALTER TABLE employees ADD COLUMN photo_url VARCHAR'))
                conn.commit()
        except Exception as e:
            print(f"SQLite schema check warning: {e}")

try:
    ensure_schema_columns()
except Exception as e:
    print(f"Schema initialization warning: {e}")

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

@app.get("/api/debug/schema")
def debug_schema(db: Session = Depends(get_db)):
    """Debug endpoint to check database schema"""
    try:
        # Get all table names
        from sqlalchemy import text
        result = db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = [row[0] for row in result]
        
        schema_info = {}
        for table in tables:
            result = db.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}' ORDER BY ordinal_position"))
            schema_info[table] = [{"name": row[0], "type": row[1], "nullable": row[2]} for row in result]
        
        return {"tables": tables, "schema": schema_info}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
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
    
    # Payroll-related summary (using timesheet data)
    year = today.year
    total_hours = db.query(func.sum(models.Timesheet.hours_worked + models.Timesheet.overtime_hours)).filter(
        models.Timesheet.date >= date(year, 1, 1),
        models.Timesheet.date <= date(year, 12, 31)
    ).scalar() or 0
    pending_timesheet_approvals = db.query(models.Timesheet).filter(models.Timesheet.approved == False).count()
    pending_leave_approvals = db.query(models.LeaveRequest).filter(models.LeaveRequest.status == "Pending").count()
    unread_notifications = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.read == False
    ).count()

    # Get list of expiring contracts
    expiring_contracts = db.query(models.Employee).filter(
        models.Employee.contract_end.between(today, thirty_days_later)
    ).all()
    
    expiring_list = [
        {
            "id": emp.id,
            "full_name": emp.full_name,
            "file_code": emp.file_code,
            "contract_end": str(emp.contract_end),
            "project": emp.project,
            "position": emp.position,
            "status": emp.status,
            "contact_number": emp.contact_number,
            "location": emp.location,
            "photo_url": emp.photo_url,
            "missing_app_resume": emp.missing_app_resume,
            "missing_appointment_letter": emp.missing_appointment_letter,
            "missing_academic_docs": emp.missing_academic_docs,
            "missing_national_id": emp.missing_national_id,
        }
        for emp in expiring_contracts
    ]

    featured_employee = expiring_list[0] if expiring_list else None
    
    return {
        "total_staff": total_staff,
        "active_staff": active_staff,
        "contracts_expiring_soon": expiring_soon,
        "staff_with_missing_docs": missing_docs,
        "project_count": project_count,
        "location_count": location_count,
        "year_to_date_hours": float(total_hours),
        "pending_leave_approvals": pending_leave_approvals,
        "pending_timesheet_approvals": pending_timesheet_approvals,
        "unread_notifications": unread_notifications,
        "expiring_contracts": expiring_list,
        "featured_employee": featured_employee
    }

# Mount static files LAST so API routes take precedence
try:
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")
