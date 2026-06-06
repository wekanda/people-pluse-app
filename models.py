from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(String)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    file_code = Column(String, unique=True, index=True)
    full_name = Column(String)
    project = Column(String)
    status = Column(String)
    position = Column(String)
    contact_number = Column(String)
    location = Column(String)
    locker = Column(String)
    date_of_appointment = Column(Date)
    contract_start = Column(Date)
    contract_end = Column(Date)
    contract_review_date = Column(Date)
    probation_end = Column(Date)
    employment_type = Column(String)
    notice_period = Column(String)
    missing_app_resume = Column(Boolean, default=False)
    missing_appointment_letter = Column(Boolean, default=False)
    missing_academic_docs = Column(Boolean, default=False)
    missing_recruitment_notes = Column(Boolean, default=False)
    missing_staff_id_form = Column(Boolean, default=False)
    missing_performance_appraisals = Column(Boolean, default=False)
    missing_national_id = Column(Boolean, default=False)
    missing_policy_declaration = Column(Boolean, default=False)
    missing_end_of_contract_notice = Column(Boolean, default=False)
    photo_url = Column(String, nullable=True)

    leave_requests = relationship("LeaveRequest", back_populates="employee")
    timesheets = relationship("Timesheet", back_populates="employee")
    appraisals = relationship("PerformanceAppraisal", back_populates="employee")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    days = Column(Float)
    reason = Column(String)
    type = Column(String)
    status = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    employee = relationship("Employee", back_populates="leave_requests")

class Timesheet(Base):
    __tablename__ = "timesheets"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    hours_worked = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    approved = Column(Boolean, default=False)
    employee = relationship("Employee", back_populates="timesheets")

class PerformanceAppraisal(Base):
    __tablename__ = "performance_appraisals"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    position = Column(String)
    duration_in_position = Column(String)
    achievements = Column(Text)
    challenges = Column(Text)
    point_outs = Column(Text)
    appraisal_date = Column(Date)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    employee = relationship("Employee", back_populates="appraisals")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    type = Column(String)
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
