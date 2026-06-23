from backend.database import SessionLocal
from backend import models

db = SessionLocal()
emp = db.query(models.Employee).filter(models.Employee.file_code == "EMP999").first()
if emp:
    print(f"SUCCESS: Employee {emp.full_name} (EMP999) was imported!")
    print(f"  Position: {emp.position}")
    print(f"  Project: {emp.project}")
    print(f"  Status: {emp.status}")
else:
    print("NO: Employee EMP999 was not imported")
db.close()
