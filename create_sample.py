import openpyxl
from datetime import date

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Employees"

headers = ["File Code", "Full Name", "Project", "Status", "Position", "Contact Number", "Location", "Date of Appointment", "Employment Type"]
ws.append(headers)

ws.append([
    "EMP999",
    "Test Employee",
    "Test Project",
    "Active",
    "Test Position",
    "0700000099",
    "Test Location",
    date.today(),
    "Full-time"
])

wb.save("uploads/sample_employees.xlsx")
print("Created uploads/sample_employees.xlsx")
