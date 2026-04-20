from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func
import models, schemas
from database import get_db
from auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/leave", tags=["leave"])

class LeaveRequestResponse(schemas.LeaveRequestCreate):
    id: int
    days: float
    status: str
    submitted_at: date
    reviewed_by: int | None = None
    class Config:
        from_attributes = True

@router.post("/request", response_model=LeaveRequestResponse)
def create_leave_request(request: schemas.LeaveRequestCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="End date must be the same or after start date")
    delta = (request.end_date - request.start_date).days + 1
    new_request = models.LeaveRequest(
        employee_id=request.employee_id,
        start_date=request.start_date,
        end_date=request.end_date,
        days=delta,
        reason=request.reason,
        type=request.type,
        status="Pending"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("/balance/{employee_id}")
def get_leave_balance(employee_id: int, db: Session = Depends(get_db)):
    total_allowed = 21
    year = date.today().year
    approved_days = db.query(func.sum(models.LeaveRequest.days)).filter(
        models.LeaveRequest.employee_id == employee_id,
        models.LeaveRequest.status == "Approved",
        models.LeaveRequest.start_date >= date(year, 1, 1),
        models.LeaveRequest.end_date <= date(year, 12, 31)
    ).scalar() or 0
    return {"total_allowed": total_allowed, "used": approved_days, "remaining": total_allowed - approved_days}

@router.get("/requests", response_model=List[LeaveRequestResponse])
def list_leave_requests(employee_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(models.LeaveRequest).order_by(models.LeaveRequest.submitted_at.desc())
    if employee_id:
        query = query.filter(models.LeaveRequest.employee_id == employee_id)
    return query.all()

@router.put("/approve/{request_id}")
def approve_leave(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Not found")
    leave.status = "Approved"
    leave.reviewed_by = current_user.id
    db.commit()
    return {"message": "Leave approved"}

@router.put("/reject/{request_id}")
def reject_leave(request_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    leave = db.query(models.LeaveRequest).filter(models.LeaveRequest.id == request_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Not found")
    leave.status = "Rejected"
    leave.reviewed_by = current_user.id
    db.commit()
    return {"message": "Leave rejected"}
