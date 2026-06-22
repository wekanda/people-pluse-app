"""
Payroll Management Router
Handles salary calculation, payroll generation, and payslip management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from database import get_db
from auth import get_current_user
import models
from typing import List

router = APIRouter(prefix="/api/payroll", tags=["payroll"])


@router.get("/employee/{employee_id}")
async def get_employee_payroll(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payroll records for an employee."""
    # Check permissions
    if current_user.role == "staff":
        if current_user.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role not in ["hr_admin", "project_manager", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    payrolls = db.query(models.Payroll).filter(
        models.Payroll.employee_id == employee_id
    ).order_by(models.Payroll.pay_period_end.desc()).all()
    
    return payrolls


@router.post("/generate")
async def generate_payroll(
    employee_id: int,
    pay_period_start: date,
    pay_period_end: date,
    basic_salary: float,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate payroll for an employee for a specific period."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Only HR/Finance can generate payroll")
    
    employee = db.query(models.Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Calculate deductions (Ugandan standards)
    # PAYE (Personal Income Tax) - simplified
    income_tax = basic_salary * 0.10  # 10% basic rate
    if basic_salary > 5000000:
        income_tax = basic_salary * 0.15
    
    # NSSF (National Social Security Fund) - 5%
    nssf_contribution = basic_salary * 0.05
    
    # Calculate gross and net
    gross_salary = basic_salary
    total_deductions = income_tax + nssf_contribution
    net_salary = gross_salary - total_deductions
    
    # Check if payroll for this period already exists
    existing = db.query(models.Payroll).filter(
        models.Payroll.employee_id == employee_id,
        models.Payroll.pay_period_start == pay_period_start,
        models.Payroll.pay_period_end == pay_period_end
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Payroll for this period already exists")
    
    payroll = models.Payroll(
        employee_id=employee_id,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        basic_salary=basic_salary,
        gross_salary=gross_salary,
        income_tax=income_tax,
        nssf_contribution=nssf_contribution,
        net_salary=net_salary,
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    
    return payroll


@router.get("/list")
async def list_payroll(
    start_date: date = None,
    end_date: date = None,
    status: str = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all payroll records (paginated)."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    query = db.query(models.Payroll)
    
    if start_date:
        query = query.filter(models.Payroll.pay_period_start >= start_date)
    if end_date:
        query = query.filter(models.Payroll.pay_period_end <= end_date)
    if status:
        query = query.filter(models.Payroll.status == status)
    
    payrolls = query.order_by(models.Payroll.pay_period_end.desc()).all()
    
    return payrolls


@router.post("/{payroll_id}/approve")
async def approve_payroll(
    payroll_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve payroll (Finance/HR only)."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    payroll = db.query(models.Payroll).get(payroll_id)
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    payroll.status = "approved"
    payroll.approved_by = current_user.id
    payroll.approved_at = datetime.utcnow()
    
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    
    return payroll


@router.post("/{payroll_id}/submit")
async def submit_payroll(
    payroll_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit payroll for approval."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    payroll = db.query(models.Payroll).get(payroll_id)
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    if payroll.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft payroll can be submitted")
    
    payroll.status = "submitted"
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    
    return payroll


@router.post("/{payroll_id}/mark-paid")
async def mark_payroll_paid(
    payroll_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark payroll as paid."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    payroll = db.query(models.Payroll).get(payroll_id)
    if not payroll:
        raise HTTPException(status_code=404, detail="Payroll not found")
    
    if payroll.status != "approved":
        raise HTTPException(status_code=400, detail="Only approved payroll can be marked as paid")
    
    payroll.status = "paid"
    db.add(payroll)
    db.commit()
    db.refresh(payroll)
    
    return payroll


@router.get("/statistics")
async def get_payroll_statistics(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payroll statistics (HR/Finance only)."""
    if current_user.role not in ["hr_admin", "finance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get current month's payroll
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)
    
    payrolls = db.query(models.Payroll).filter(
        models.Payroll.pay_period_start >= month_start,
        models.Payroll.pay_period_end <= month_end
    ).all()
    
    total_gross = sum(p.gross_salary for p in payrolls)
    total_net = sum(p.net_salary for p in payrolls)
    total_tax = sum(p.income_tax for p in payrolls)
    total_nssf = sum(p.nssf_contribution for p in payrolls)
    
    return {
        "period": f"{month_start.strftime('%B %Y')}",
        "total_employees": len(set(p.employee_id for p in payrolls)),
        "total_gross_salary": total_gross,
        "total_deductions": total_tax + total_nssf,
        "total_net_salary": total_net,
        "total_income_tax": total_tax,
        "total_nssf": total_nssf,
        "records_count": len(payrolls),
        "pending": sum(1 for p in payrolls if p.status == "draft"),
        "submitted": sum(1 for p in payrolls if p.status == "submitted"),
        "approved": sum(1 for p in payrolls if p.status == "approved"),
        "paid": sum(1 for p in payrolls if p.status == "paid")
    }
