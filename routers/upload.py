from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import openpyxl
from datetime import datetime
import models
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/upload", tags=["upload"])

HEADER_MAP = {
    "file code": "file_code",
    "employee code": "file_code",
    "staff no": "file_code",
    "project": "project",
    "full name": "full_name",
    "name": "full_name",
    "status": "status",
    "position": "position",
    "location": "location",
    "site": "location",
    "contact": "contact_number",
    "contact number": "contact_number",
    "phone": "contact_number",
    "locker": "locker",
    "date of appointment": "date_of_appointment",
    "appointment date": "date_of_appointment",
    "contract start": "contract_start",
    "contract end": "contract_end",
    "contract review date": "contract_review_date",
    "review date": "contract_review_date",
    "probation end": "probation_end",
    "notice period": "notice_period",
    "employment type": "employment_type",
    "missing application/resume": "missing_app_resume",
    "missing app resume": "missing_app_resume",
    "missing appointment letter": "missing_appointment_letter",
    "missing academic docs": "missing_academic_docs",
    "missing recruitment notes": "missing_recruitment_notes",
    "missing staff id form": "missing_staff_id_form",
    "missing performance appraisals": "missing_performance_appraisals",
    "missing national id": "missing_national_id",
    "missing policy declaration": "missing_policy_declaration",
    "missing end of contract notice": "missing_end_of_contract_notice",
}

BOOL_KEYS = {
    "yes",
    "true",
    "1",
    "x",
    "y",
    "present",
    "missing",
}

@router.post("/excel")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        if current_user.role != "hr_admin":
            raise HTTPException(status_code=403, detail="Only HR admin can upload")

        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")

        workbook = openpyxl.load_workbook(file.file)
        imported = 0
        for sheet in workbook.worksheets:
            header_row_index, headers = _find_headers(sheet)
            if not headers:
                continue
            for row in sheet.iter_rows(min_row=header_row_index + 1, values_only=True):
                row_data = _map_row_data(headers, row)
                if not row_data.get("file_code") or not row_data.get("full_name"):
                    continue
                row_data = _normalize_row_data(row_data)
                existing = db.query(models.Employee).filter(models.Employee.file_code == row_data["file_code"]).first()
                if existing:
                    for key, value in row_data.items():
                        if hasattr(existing, key) and value is not None:
                            setattr(existing, key, value)
                else:
                    db.add(models.Employee(**row_data))
                imported += 1

        db.commit()
        return {"message": f"Imported/updated {imported} records"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Upload error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def _find_headers(sheet):
    for row_index, row in enumerate(sheet.iter_rows(min_row=1, max_row=12, values_only=True), start=1):
        if not row:
            continue
        normalized = [str(cell).strip().lower() if cell is not None else "" for cell in row]
        if any(key in normalized for key in ("file code", "full name", "project", "contact")):
            return row_index, [HEADER_MAP.get(cell.strip().lower(), None) if cell else None for cell in normalized]
    return None, []


def _map_row_data(headers, row):
    data = {}
    for idx, key in enumerate(headers):
        if key:
            data[key] = row[idx] if idx < len(row) else None
    return data


def _normalize_row_data(data):
    normalized = {}
    for key, value in data.items():
        if value is None:
            normalized[key] = None
            continue
        if key in {"missing_app_resume", "missing_appointment_letter", "missing_academic_docs", "missing_recruitment_notes", "missing_staff_id_form", "missing_performance_appraisals", "missing_national_id", "missing_policy_declaration", "missing_end_of_contract_notice"}:
            normalized[key] = _parse_bool(value)
        elif key in {"date_of_appointment", "contract_start", "contract_end", "contract_review_date", "probation_end"}:
            normalized[key] = _parse_date(value)
        else:
            normalized[key] = str(value).strip() if isinstance(value, str) else value
    return normalized


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in BOOL_KEYS


def _parse_date(val):
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        text = val.strip()
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y"]:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
    return None
