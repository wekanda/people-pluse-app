# Phase 1 Models: Role-Based Access Control, e-PFile, Leave Management

# Add these to the end of models.py

class LeaveType(Base):
    """Define leave types and their entitlements per Ugandan labor standards."""
    __tablename__ = "leave_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # Annual, Sick, Maternity, Paternity, etc.
    annual_entitlement_days = Column(Float)  # Days per year
    description = Column(String, nullable=True)
    is_paid = Column(Boolean, default=True)
    requires_manager_approval = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LeaveBalance(Base):
    """Track leave balance for each employee per leave type."""
    __tablename__ = "leave_balances"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), index=True)
    balance = Column(Float, default=0.0)  # Days remaining
    accrued = Column(Float, default=0.0)  # Days earned this year
    used = Column(Float, default=0.0)  # Days used this year
    last_updated = Column(DateTime, default=datetime.utcnow)
    employee = relationship("Employee", backref="leave_balances")
    leave_type = relationship("LeaveType")


class DocumentType(Base):
    """Define required document types for personnel files (e-PFile)."""
    __tablename__ = "document_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # National ID, Contract, etc.
    category = Column(String)  # personal, employment, qualification, medical, etc.
    is_required = Column(Boolean, default=True)  # Flag if document is mandatory
    expiry_period_days = Column(Integer, nullable=True)  # Days until expiry (None = never)
    created_at = Column(DateTime, default=datetime.utcnow)


class EmployeeDocument(Base):
    """Track documents per employee for e-PFile (Electronic Personnel File)."""
    __tablename__ = "employee_documents"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.id"), index=True)
    file_path = Column(String)  # Relative path in uploads/
    file_name = Column(String)
    uploaded_by = Column(Integer, ForeignKey("users.id"))  # User who uploaded
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    approved = Column(Boolean, default=False)  # P&C approval status
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    expiry_date = Column(Date, nullable=True)  # For certificates, contracts, etc.
    is_expired = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    employee = relationship("Employee", backref="documents")
    document_type = relationship("DocumentType")
    uploader = relationship("User", foreign_keys=[uploaded_by], backref="uploaded_documents")
    approver = relationship("User", foreign_keys=[approved_by], backref="approved_documents")
