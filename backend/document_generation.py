from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from auth import get_current_user
from datetime import datetime
from typing import Optional
import json
import os
from pathlib import Path
from fastapi.responses import FileResponse

router = APIRouter(prefix="/documents", tags=["documents"])


def _resolve_documents_base(subpath: Optional[str] = None) -> Path:
    """Return the preferred base folder for documents. Prefer `documents/`,
    otherwise fall back to `uploads/documents` or `uploads` as a safe location."""
    repo_root = Path(__file__).resolve().parents[2]
    candidates = [repo_root / "documents", repo_root / "uploads" / "documents", repo_root / "uploads"]
    for c in candidates:
        base = (c / subpath) if subpath and c.exists() else (c if not subpath else None)
        if base and base.exists():
            return base.resolve()
    # If none exist, return the first candidate path where we will create folders when needed
    return (repo_root / "uploads" / (subpath or "")).resolve()


@router.get('/policies')
def get_document_policies(current_user=Depends(get_current_user)):
    """Return stored document policies. Accessible to any authenticated user."""
    repo_root = Path(__file__).resolve().parents[2]
    policies_file = repo_root / 'uploads' / 'doc_policies.json'
    if not policies_file.exists():
        # default policies
        default = {"allow_project_manager_uploads": False, "allow_staff_uploads": False}
        return default
    try:
        data = json.loads(policies_file.read_text(encoding='utf-8'))
        return data
    except Exception:
        return {"allow_project_manager_uploads": False, "allow_staff_uploads": False}


@router.post('/policies')
def set_document_policies(payload: dict, current_user=Depends(get_current_user)):
    """Persist document policies. Only `hr_admin` may update policies."""
    if current_user.role != 'hr_admin':
        raise HTTPException(status_code=403, detail='Only hr_admin may update policies')
    repo_root = Path(__file__).resolve().parents[2]
    uploads = repo_root / 'uploads'
    uploads.mkdir(parents=True, exist_ok=True)
    policies_file = uploads / 'doc_policies.json'
    # accept only known keys
    allowed_keys = {"allow_project_manager_uploads", "allow_staff_uploads"}
    data = {k: bool(payload.get(k, False)) for k in allowed_keys}
    try:
        policies_file.write_text(json.dumps(data, indent=2), encoding='utf-8')
        return {"ok": True, "policies": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document templates
TEMPLATES = {
    "appointment_letter": """
APPOINTMENT LETTER

Date: {date}

To: {employee_name}
    {employee_email}
    {employee_address}

Dear {employee_name},

We are pleased to offer you the position of {position} at People Plus HR Systems.

Position Details:
- Position: {position}
- Department: {department}
- Start Date: {start_date}
- Employment Type: {employment_type}
- Reporting To: {manager_name}

Compensation:
- Annual Salary: {currency} {salary}
- Benefits: {benefits}

Terms of Employment:
1. This is an employment relationship subject to the laws of Kenya.
2. Your employment is subject to satisfactory completion of background checks and verification.
3. You will be subject to our company policies as per the employee handbook.

We look forward to welcoming you to our team.

Best regards,

Human Resources Manager
People Plus HR Systems
""",

    "offer_letter": """
OFFER OF EMPLOYMENT

Date: {date}

Dear {applicant_name},

We are pleased to make you a formal offer of employment for the position of {position} at People Plus HR Systems.

Position Details:
- Job Title: {position}
- Department: {department}
- Location: {location}
- Proposed Start Date: {start_date}
- Employment Type: {employment_type}

Compensation Package:
- Base Salary: {currency} {base_salary} per annum
- Other Benefits: {benefits}
- Annual Leave: 21 days

Your responsibilities will include:
{responsibilities}

Conditions of Employment:
1. This offer is conditional upon successful background verification.
2. You are required to provide proof of educational qualifications.
3. A medical examination may be required.
4. You will be required to sign our standard employment contract.

If you accept this offer, please confirm your acceptance by {acceptance_deadline}.

We look forward to your response.

Sincerely,

Human Resources Department
People Plus HR Systems
""",

    "contract": """
EMPLOYMENT AGREEMENT

This Employment Agreement is entered into on {date} between:

PEOPLE PLUS HR SYSTEMS (hereinafter "Employer")

AND

{employee_name} (hereinafter "Employee")

WHEREAS, the Employer wishes to employ the Employee and the Employee wishes to be employed by the Employer on the terms and conditions set forth herein:

1. POSITION
The Employee shall be employed as a {position} in the {department} department.

2. TERM
The employment shall commence on {start_date} and shall continue until terminated as per the provisions herein.

3. COMPENSATION
The Employee shall receive an annual salary of {currency} {salary}, payable in monthly installments.

4. BENEFITS
The Employee shall be entitled to:
- Annual leave of 21 days
- Health insurance coverage
- Pension contributions
- Other benefits as per company policy

5. DUTIES AND RESPONSIBILITIES
The Employee shall perform duties as assigned by management consistent with the position of {position}.

6. CONFIDENTIALITY
The Employee agrees to maintain confidentiality of all company information.

7. TERMINATION
Either party may terminate this agreement by giving 30 days written notice.

8. DISPUTE RESOLUTION
Disputes arising from this agreement shall be governed by the laws of Kenya.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

EMPLOYER:                          EMPLOYEE:

_____________________            _____________________
{employer_name}                  {employee_name}
Authorized Signatory             

Date: _______________            Date: _______________
""",

    "separation_letter": """
LETTER OF SEPARATION / TERMINATION OF EMPLOYMENT

Date: {date}

To: {employee_name}
    {employee_email}

Dear {employee_name},

This letter confirms the termination of your employment with People Plus HR Systems effective {termination_date}.

Reason for Termination: {reason}

Final Paycheck:
Your final paycheck, including accrued leave and any severance as per company policy, will be processed by {payout_date}.

Items to Return:
Please ensure the following items are returned on or before your last day:
- Employee ID Card
- Office Access Card
- Company Equipment (Laptop, Phone, etc.)
- Any other company property

Outstanding Benefits:
{benefits_info}

Reference:
We appreciate your service and will provide employment reference upon request.

If you have any questions, please contact the Human Resources department.

Sincerely,

Human Resources Manager
People Plus HR Systems
"""
}


@router.post("/generate")
def generate_document(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Generate a document from template (appointment letter, contract, offer letter, etc.)"""
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    template_type = payload.get("template_type", "").lower()
    if template_type not in TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Template not found. Available: {', '.join(TEMPLATES.keys())}")
    
    template = TEMPLATES[template_type]
    
    # Get employee/applicant details
    employee_id = payload.get("employee_id")
    applicant_id = payload.get("applicant_id")
    
    employee = None
    applicant = None
    if employee_id:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if applicant_id:
        applicant = db.query(models.Application).filter(models.Application.id == applicant_id).first()
    
    # Build substitution context
    context = {
        "date": datetime.utcnow().strftime("%d %B %Y"),
        "employee_name": employee.full_name if employee else applicant.applicant_name if applicant else "",
        "employee_email": employee.email if employee else applicant.email if applicant else "",
        "employee_address": getattr(employee, 'address', 'Not provided') if employee else "",
        "applicant_name": applicant.applicant_name if applicant else "",
        "position": payload.get("position", "Position Title"),
        "department": payload.get("department", "Department"),
        "location": payload.get("location", "Not specified"),
        "start_date": payload.get("start_date", "To be confirmed"),
        "employment_type": payload.get("employment_type", "Full-time"),
        "currency": payload.get("currency", "KES"),
        "salary": payload.get("salary", "Confidential"),
        "base_salary": payload.get("base_salary", "Confidential"),
        "manager_name": payload.get("manager_name", "Your Manager"),
        "employer_name": payload.get("employer_name", "HR Director"),
        "benefits": payload.get("benefits", "As per company policy"),
        "responsibilities": payload.get("responsibilities", "As defined by management"),
        "acceptance_deadline": payload.get("acceptance_deadline", "Within 5 business days"),
        "termination_date": payload.get("termination_date", "To be confirmed"),
        "payout_date": payload.get("payout_date", "Within 30 days"),
        "reason": payload.get("reason", "As per company notice"),
        "benefits_info": payload.get("benefits_info", "As per final settlement"),
    }
    
    # Generate document by substituting placeholders
    try:
        html_content = template.format(**context)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    
    # Log document generation
    log = models.AuditLog(
        user_id=current_user.id,
        action="document_generated",
        object_type=template_type,
        object_id=str(employee_id or applicant_id),
        details=json.dumps(context)
    )
    db.add(log)
    db.commit()
    
    return {
        "template_type": template_type,
        "content": html_content,
        "generated_at": datetime.utcnow().isoformat(),
        "generated_by": current_user.full_name
    }


@router.post("/send")
def send_document(payload: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    template_type = payload.get("template_type", "").lower()
    email = payload.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Recipient email is required")
    if template_type not in TEMPLATES:
        raise HTTPException(status_code=400, detail=f"Template not found. Available: {', '.join(TEMPLATES.keys())}")

    template = TEMPLATES[template_type]
    employee_id = payload.get("employee_id")
    applicant_id = payload.get("applicant_id")

    employee = None
    applicant = None
    if employee_id:
        employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if applicant_id:
        applicant = db.query(models.Application).filter(models.Application.id == applicant_id).first()

    context = {
        "date": datetime.utcnow().strftime("%d %B %Y"),
        "employee_name": employee.full_name if employee else applicant.applicant_name if applicant else "",
        "employee_email": employee.email if employee else applicant.email if applicant else "",
        "employee_address": getattr(employee, 'address', 'Not provided') if employee else "",
        "applicant_name": applicant.applicant_name if applicant else "",
        "position": payload.get("position", "Position Title"),
        "department": payload.get("department", "Department"),
        "location": payload.get("location", "Not specified"),
        "start_date": payload.get("start_date", "To be confirmed"),
        "employment_type": payload.get("employment_type", "Full-time"),
        "currency": payload.get("currency", "KES"),
        "salary": payload.get("salary", "Confidential"),
        "base_salary": payload.get("base_salary", "Confidential"),
        "manager_name": payload.get("manager_name", "Your Manager"),
        "employer_name": payload.get("employer_name", "HR Director"),
        "benefits": payload.get("benefits", "As per company policy"),
        "responsibilities": payload.get("responsibilities", "As defined by management"),
        "acceptance_deadline": payload.get("acceptance_deadline", "Within 5 business days"),
        "termination_date": payload.get("termination_date", "To be confirmed"),
        "payout_date": payload.get("payout_date", "Within 30 days"),
        "reason": payload.get("reason", "As per company notice"),
        "benefits_info": payload.get("benefits_info", "As per final settlement"),
    }

    try:
        html_content = template.format(**context)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")

    uploads_dir = Path(__file__).resolve().parents[2] / "uploads" / "sent_documents"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    send_file = uploads_dir / f"{template_type}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.html"
    send_file.write_text(html_content, encoding="utf-8")

    log = models.AuditLog(
        user_id=current_user.id,
        action="document_sent",
        object_type=template_type,
        object_id=email,
        details=json.dumps({"email": email, "template_type": template_type, "context": context})
    )
    db.add(log)
    db.commit()

    return {
        "message": f"Document {template_type} ready to send to {email}",
        "saved_path": str(send_file.relative_to(Path(__file__).resolve().parents[2]))
    }


@router.get("/templates")
def list_available_templates(current_user=Depends(get_current_user)):
    """List all available document templates"""
    if current_user.role not in ["hr_admin", "project_manager"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "templates": list(TEMPLATES.keys()),
        "count": len(TEMPLATES),
        "descriptions": {
            "appointment_letter": "Letter confirming a new employee's appointment",
            "offer_letter": "Formal job offer to a candidate",
            "contract": "Employment contract with terms and conditions",
            "separation_letter": "Formal separation/termination letter"
        }
    }


@router.get("/files")
def list_document_files(current_user=Depends(get_current_user)):
    """List all files under the repository `documents` folder (docx/xlsx/pdf).
    Returns relative paths so the frontend can request downloads."""
    base = _resolve_documents_base()
    files = []
    if base.exists():
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".docx", ".doc", ".xlsx", ".xls", ".pdf"]:
                files.append({
                    "name": p.name,
                    # return paths relative to the selected base so downloads resolve correctly
                    "relative_path": str(p.relative_to(base)).replace('\\', '/'),
                    "suffix": p.suffix.lower()
                })

    return {"count": len(files), "files": files}


@router.get("/files/download")
def download_document_file(file_path: str, current_user=Depends(get_current_user)):
    """Download a file from the `documents` folder. Protects against path traversal."""
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path query parameter is required")
    base = _resolve_documents_base()
    target = (base / file_path).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(target), filename=target.name, media_type="application/octet-stream")


@router.get("/sent")
def list_sent_documents(current_user=Depends(get_current_user)):
    """List all generated/sent documents from the sent_documents folder."""
    base = _resolve_documents_base(subpath="sent_documents")
    files = []
    if base.exists():
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".docx", ".doc", ".xlsx", ".xls", ".pdf"]:
                files.append({
                    "name": p.name,
                    # relative to the repo root so frontend can request /documents/sent/download?file_path=...
                    "relative_path": str(p.relative_to(Path(__file__).resolve().parents[2])).replace('\\', '/'),
                    "created_at": datetime.fromtimestamp(p.stat().st_mtime).isoformat()
                })

    return {"count": len(files), "files": sorted(files, key=lambda x: x.get("created_at", ""), reverse=True)}


@router.get("/sent/download")
def download_sent_document(file_path: str, current_user=Depends(get_current_user)):
    """Download a sent/generated document from the sent_documents folder."""
    if not file_path:
        raise HTTPException(status_code=400, detail="file_path query parameter is required")
    base = _resolve_documents_base(subpath="sent_documents")
    repo_root = Path(__file__).resolve().parents[2]
    # allow file_path to be relative to repo_root or to the sent_documents base
    candidate = repo_root / file_path
    if candidate.exists() and candidate.is_file():
        target = candidate.resolve()
    else:
        target = (base / file_path).resolve()

    if not str(target).startswith(str(base)) and not str(target).startswith(str(repo_root)):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=str(target), filename=target.name, media_type="application/octet-stream")

