from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel
import models
from database import get_db
from auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/appraisal", tags=["appraisal"])

class AppraisalCreate(BaseModel):
    employee_id: int
    position: str
    duration_in_position: str
    achievements: str
    challenges: str
    point_outs: str = None

class AppraisalResponse(BaseModel):
    id: int
    employee_id: int
    position: str
    duration_in_position: str | None = None
    achievements: str
    challenges: str
    point_outs: str | None = None
    appraisal_date: date
    class Config:
        from_attributes = True

@router.post("/create", response_model=AppraisalResponse)
def create_appraisal(appraisal: AppraisalCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_appraisal = models.PerformanceAppraisal(
        **appraisal.dict(),
        appraisal_date=date.today(),
        reviewer_id=current_user.id
    )
    db.add(db_appraisal)
    db.commit()
    db.refresh(db_appraisal)
    return db_appraisal

@router.get("/employee/{employee_id}", response_model=List[AppraisalResponse])
def get_employee_appraisals(employee_id: int, db: Session = Depends(get_db)):
    return db.query(models.PerformanceAppraisal).filter(models.PerformanceAppraisal.employee_id == employee_id).all()

@router.get("/{appraisal_id}", response_model=AppraisalResponse)
def get_appraisal(appraisal_id: int, db: Session = Depends(get_db)):
    appraisal = db.query(models.PerformanceAppraisal).filter(models.PerformanceAppraisal.id == appraisal_id).first()
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
    return appraisal
