"""
Employee Documents Router - Phase 1 e-PFile
Manages electronic personnel files (ePFile) with document upload, approval, and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import shutil
import os
from database import get_db
from auth import get_current_user, check_employee_access
import models

router = APIRouter(prefix="/employees", tags=["employee-documents"])

UPLOAD_DIR = Path("uploads/employee_documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==================== SCHEMAS ====================

class DocumentTypeSchema(BaseModel):
    id: int
    name: str
    category: str
    is_required: bool
    expiry_period_days: Optional[int] = None

    class Config:
        from_attributes = True


class EmployeeDocumentSchema(BaseModel):
    id: int
    employee_id: int
    document_type_id: int
    document_type: Optional[DocumentTypeSchema] = None
    file_name: str
    uploaded_at: datetime
    approved: bool
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    expiry_date: Optional[date] = None
    is_expired: bool
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeFileSummarySchema(BaseModel):
    employee_id: int
    total_required_documents: int
    uploaded_documents: int
    approved_documents: int
    expired_documents: int
    missing_required_documents: List[str]
    completeness_percentage: float

    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.get("/{employee_id}/documents", response_model=List[EmployeeDocumentSchema])
async def list_employee_documents(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents in an employee's e-PFile."""
    if not check_employee_access(current_user, employee_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's documents"
        )
    
    documents = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id
    ).all()
    
    return documents


@router.post("/{employee_id}/documents", response_model=EmployeeDocumentSchema)
async def upload_employee_document(
    employee_id: int,
    document_type_id: int = Form(...),
    file: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    expiry_date: Optional[date] = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a document to employee's e-PFile.
    
    HR Admin can upload for any employee.
    Managers can upload for their team.
    Staff can upload their own documents.
    """
    if not check_employee_access(current_user, employee_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload documents for this employee"
        )
    
    # Verify employee exists
    employee = db.query(models.Employee).filter(
        models.Employee.id == employee_id
    ).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Verify document type exists
    doc_type = db.query(models.DocumentType).filter(
        models.DocumentType.id == document_type_id
    ).first()
    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found"
        )
    
    # Save file
    employee_upload_dir = UPLOAD_DIR / str(employee_id)
    employee_upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix
    saved_filename = f"{doc_type.name.replace(' ', '_')}_{timestamp}{file_ext}"
    file_path = employee_upload_dir / saved_filename
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Create document record
    db_document = models.EmployeeDocument(
        employee_id=employee_id,
        document_type_id=document_type_id,
        file_path=f"employee_documents/{employee_id}/{saved_filename}",
        file_name=file.filename,
        uploaded_by=current_user.id,
        uploaded_at=datetime.utcnow(),
        expiry_date=expiry_date,
        is_expired=False,
        notes=notes,
        approved=current_user.role == "hr_admin",  # Auto-approve HR Admin uploads
        approved_by=current_user.id if current_user.role == "hr_admin" else None,
        approved_at=datetime.utcnow() if current_user.role == "hr_admin" else None
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document


@router.get("/{employee_id}/documents/{document_id}", response_model=EmployeeDocumentSchema)
async def get_document(
    employee_id: int,
    document_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific document."""
    if not check_employee_access(current_user, employee_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's documents"
        )
    
    document = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.id == document_id,
        models.EmployeeDocument.employee_id == employee_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return document


@router.patch("/{employee_id}/documents/{document_id}/approve")
async def approve_document(
    employee_id: int,
    document_id: int,
    notes: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a document (HR Admin or P&C Manager only)."""
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR Admin or managers can approve documents"
        )
    
    document = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.id == document_id,
        models.EmployeeDocument.employee_id == employee_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.approved = True
    document.approved_by = current_user.id
    document.approved_at = datetime.utcnow()
    document.notes = notes or document.notes
    
    db.commit()
    db.refresh(document)
    
    return {
        "status": "success",
        "message": "Document approved",
        "document": document
    }


@router.delete("/{employee_id}/documents/{document_id}")
async def delete_document(
    employee_id: int,
    document_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document (HR Admin only)."""
    if current_user.role != "hr_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR Admin can delete documents"
        )
    
    document = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.id == document_id,
        models.EmployeeDocument.employee_id == employee_id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file
    try:
        file_path = Path("uploads") / document.file_path
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Warning: Failed to delete file: {str(e)}")
    
    # Delete record
    db.delete(document)
    db.commit()
    
    return {"status": "success", "message": "Document deleted"}


@router.get("/{employee_id}/file-summary", response_model=EmployeeFileSummarySchema)
async def get_file_summary(
    employee_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get e-PFile completeness summary for an employee."""
    if not check_employee_access(current_user, employee_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this employee's file summary"
        )
    
    # Get all required document types
    required_types = db.query(models.DocumentType).filter(
        models.DocumentType.is_required == True
    ).all()
    
    # Get employee's documents
    employee_docs = db.query(models.EmployeeDocument).filter(
        models.EmployeeDocument.employee_id == employee_id
    ).all()
    
    # Check expiry dates
    today = date.today()
    for doc in employee_docs:
        if doc.expiry_date and doc.expiry_date < today:
            doc.is_expired = True
    
    db.commit()
    
    # Calculate statistics
    uploaded_count = len(employee_docs)
    approved_count = len([d for d in employee_docs if d.approved])
    expired_count = len([d for d in employee_docs if d.is_expired])
    
    # Find missing required documents
    uploaded_type_ids = set(d.document_type_id for d in employee_docs)
    missing_types = [
        t.name for t in required_types
        if t.id not in uploaded_type_ids
    ]
    
    completeness = (
        (len(required_types) - len(missing_types)) / len(required_types) * 100
    ) if required_types else 0
    
    return EmployeeFileSummarySchema(
        employee_id=employee_id,
        total_required_documents=len(required_types),
        uploaded_documents=uploaded_count,
        approved_documents=approved_count,
        expired_documents=expired_count,
        missing_required_documents=missing_types,
        completeness_percentage=round(completeness, 2)
    )


@router.get("/document-types/all", response_model=List[DocumentTypeSchema])
async def list_document_types(db: Session = Depends(get_db)):
    """Get all available document types."""
    types = db.query(models.DocumentType).all()
    return types
