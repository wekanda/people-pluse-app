"""
Document Management Router
Handles employee documents, e-PFile, document approvals, and audit trails
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from database import get_db
from auth import get_current_user
import models
import os
from pathlib import Path

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/types")
async def get_document_types(db: Session = Depends(get_db)):
    """Get all document types required for personnel files."""
    types = db.query(models.DocumentType).all()
    return types


@router.post("/types")
async def create_document_type(
    name: str,
    category: str,
    is_required: bool = True,
    expiry_period_days: int = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document type (Admin only)."""
    if current_user.role != "hr_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    doc_type = models.DocumentType(
        name=name,
        category=category,
        is_required=is_required,
        expiry_period_days=expiry_period_days
    )
    db.add(doc_type)
    db.commit()
    db.refresh(doc_type)
    return doc_type


@router.post("/upload")
async def upload_document(
    employee_id: int,
    document_type_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document for an employee's personnel file."""
    # Verify access
    employee = db.query(models.Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check permissions
    if current_user.role not in ["hr_admin", "project_manager"]:
        if current_user.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    # Save file
    file_path = UPLOAD_DIR / f"{employee_id}_{document_type_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Create document record
    doc = models.EmployeeDocument(
        employee_id=employee_id,
        document_type_id=document_type_id,
        file_path=str(file_path),
        file_name=file.filename,
        uploaded_by=current_user.id,
        approval_status="pending" if current_user.role == "staff" else "approved",
        approved_by=current_user.id if current_user.role != "staff" else None,
        approved_at=datetime.utcnow() if current_user.role != "staff" else None
    )
    db.add(doc)
    
    # Create audit record
    audit = models.DocumentAudit(
        employee_document_id=None,  # Will update after commit
        action="uploaded",
        performed_by=current_user.id,
        details=f"Uploaded {file.filename}"
    )
    db.add(audit)
    db.commit()
    db.refresh(doc)
    audit.employee_document_id = doc.id
    db.commit()
    
    # Update personnel file completeness
    update_personnel_file_completeness(employee_id, db)
    
    return doc


@router.get("/employee/{employee_id}")
async def get_employee_documents(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all documents for an employee."""
    employee = db.query(models.Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check permissions
    if current_user.role == "staff":
        if current_user.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    
    documents = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id
    ).all()
    
    return documents


@router.post("/{doc_id}/approve")
async def approve_document(
    doc_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a document (HR/Manager only)."""
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    doc = db.query(models.EmployeeDocument).get(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc.approval_status = "approved"
    doc.approved_by = current_user.id
    doc.approved_at = datetime.utcnow()
    db.add(doc)
    
    # Create audit record
    audit = models.DocumentAudit(
        employee_document_id=doc_id,
        action="approved",
        performed_by=current_user.id
    )
    db.add(audit)
    db.commit()
    
    # Update personnel file completeness
    update_personnel_file_completeness(doc.employee_id, db)
    
    return doc


@router.get("/personnel-file/{employee_id}")
async def get_personnel_file(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee's electronic personnel file (e-PFile) summary."""
    employee = db.query(models.Employee).get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Get or create personnel file
    pfile = db.query(models.PersonnelFile).filter(
        models.PersonnelFile.employee_id == employee_id
    ).first()
    
    if not pfile:
        pfile = models.PersonnelFile(employee_id=employee_id)
        db.add(pfile)
        db.commit()
    
    # Get all documents
    documents = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id
    ).all()
    
    # Get required documents
    required_docs = db.query(models.DocumentType).filter(
        models.DocumentType.is_required == True
    ).all()
    
    # Calculate completeness
    approved_count = sum(1 for d in documents if d.approval_status == "approved")
    completeness = (approved_count / len(required_docs) * 100) if required_docs else 0
    
    pfile.completeness_percentage = completeness
    db.commit()
    
    return {
        "personnel_file": pfile,
        "documents": documents,
        "required_documents": required_docs,
        "completeness_percentage": completeness,
        "approved_documents": approved_count,
        "total_required": len(required_docs)
    }


def update_personnel_file_completeness(employee_id: int, db: Session):
    """Update personnel file completeness percentage."""
    pfile = db.query(models.PersonnelFile).filter(
        models.PersonnelFile.employee_id == employee_id
    ).first()
    
    if not pfile:
        pfile = models.PersonnelFile(employee_id=employee_id)
        db.add(pfile)
    
    # Count approved documents
    approved_docs = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id,
        models.EmployeeDocument.approval_status == "approved"
    ).count()
    
    # Count required documents
    required_docs = db.query(models.DocumentType).filter(
        models.DocumentType.is_required == True
    ).count()
    
    if required_docs > 0:
        pfile.completeness_percentage = (approved_docs / required_docs) * 100
    
    # Check for expired documents
    expired_docs = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id,
        models.EmployeeDocument.expiry_date < date.today()
    ).all()
    
    pfile.flagged_expired_count = len(expired_docs)
    
    # Check for missing documents
    missing = db.query(models.DocumentType).filter(
        models.DocumentType.is_required == True,
        ~models.DocumentType.id.in_(
            db.query(models.EmployeeDocument.document_type_id).filter(
                models.EmployeeDocument.employee_id == employee_id,
                models.EmployeeDocument.approval_status == "approved"
            )
        )
    ).all()
    
    pfile.flagged_missing_count = len(missing)
    pfile.missing_documents = ", ".join([d.name for d in missing])
    pfile.last_updated = datetime.utcnow()
    
    db.commit()


@router.get("/audit-trail/{employee_id}")
async def get_document_audit_trail(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get audit trail for employee documents."""
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    audits = db.query(models.DocumentAudit).join(
        models.EmployeeDocument
    ).filter(
        models.EmployeeDocument.employee_id == employee_id
    ).order_by(models.DocumentAudit.performed_at.desc()).all()
    
    return audits
