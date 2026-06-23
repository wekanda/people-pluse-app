from pydantic import BaseModel
from datetime import date
class LeaveRequestCreate(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: str
    type: str

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str
    employee_id: int | None = None
