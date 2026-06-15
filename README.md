# PEOPLE PLUSE - Comprehensive HR & Recruitment Management System

A full-stack HR management platform built with FastAPI (backend), React (frontend), and SQLAlchemy ORM. Features complete recruitment lifecycle management, internship tracking, payroll processing, employee management, and compliance auditing.

**Status: ✅ PRODUCTION READY - MVP v1.0.0**

## 🚀 Quick Start

### Backend (5 minutes)
```bash
cd backend
pip install -r requirements.txt
python main.py  # Runs at http://localhost:8000
```

### Frontend (5 minutes)
```bash
cd frontend
npm install
npm run dev  # Runs at http://localhost:5173
```

### Test Credentials
- Admin: live_admin@peoplepluse.com / admin123
- Manager: live_manager@peoplepluse.com / manager123
- Staff: live_staff@peoplepluse.com / staff123
- Finance: finance@peoplepluse.com / finance123

---

## Features

### 🎯 Core HR Functions
- **Recruitment Management**: Job posting, applicant tracking, interview scheduling, offer management
- **Applicant Tracking System (ATS)**: Full pipeline management (screening → interviews → offers → onboarding)
- **Talent Pool & Referrals**: Maintain and search candidate database
- **Resume Parsing**: PDF/text extraction with AI-like keyword detection
- **Interview Management**: ICS calendar invite generation + Interview Scheduling page (NEW)
- **Assessments & Testing**: Customizable assessment templates with automated scoring
- **Onboarding Checklists**: Structured pre-boarding task management with progress tracking (NEW)

### 💼 Employee Management
- Staff directory with photo/document management
- Timesheet tracking and approval workflows
- Leave request management with multi-level approvals + Team Calendar View (NEW)
- Performance appraisals with analytics (NEW)
- Document management with persistence to disk

### 💰 Payroll & Finance
- Automated payslip generation (PDF & Excel export)
- Excel-based bulk payslip import with validation
- Financial reporting and analytics (NEW - 5 reporting modules)
- Per-user financial dashboards
- CSV export for accounting systems

### 🔒 Compliance & Security
- Role-based access control with ProtectedRoute guards (NEW)
- Comprehensive audit logging and export (ENHANCED)
- GDPR data processing consent tracking
- Background verification tracking
- Offer signing workflow (DocuSign stub)
- Contract expiry alerting (30/60/90 days) (NEW)

### 📊 Advanced Features (NEW)
- **Analytics Dashboard** - HR metrics, recruitment stats, payroll analysis, performance distribution
- **Contract Generation** - Automated templates (appointments, offers, contracts, separation letters)
- **Compliance Dashboard** - Audit logs, compliance metrics, data export

### 📱 Multi-role Dashboards
- Admin dashboard: Overall metrics, expiring contracts, missing documents
- User dashboard: Personal payslips, leave balance, appraisals
- Finance dashboard: Payroll summaries, reports, exports
- HR dashboard: Recruitment pipeline, analytics, compliance

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0+
- **Database**: SQLite (dev), PostgreSQL (production)
- **Authentication**: JWT + bcrypt
- **File Processing**: openpyxl (Excel), pdfminer.six (PDF parsing)

### Frontend
- **Framework**: React 18 (Vite)
- **UI Library**: Material-UI (MUI)
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: Material-UI + CSS

## Project Structure

```
people-pluse-app/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # Data models
│   ├── auth.py                 # JWT authentication
│   ├── auth_router.py          # Auth endpoints
│   ├── requirements.txt        # Python dependencies
│   ├── routers/
│   │   ├── recruitment.py      # Job posting & applications
│   │   ├── ats.py              # ATS pipeline, resume parsing, interviews
│   │   ├── hr_tools.py         # Talent pool, referrals, screening, offers
│   │   ├── calendar_integration.py  # Calendar stubs (Google/Microsoft)
│   │   ├── assessments.py      # Assessment templates & scoring
│   │   ├── finance.py          # Payroll & reporting
│   │   ├── upload.py           # Excel/resume file uploads
│   │   ├── requisition.py      # Job requisition workflow
│   │   ├── employees.py        # Staff directory
│   │   ├── leave.py            # Leave management
│   │   ├── timesheet.py        # Time tracking
│   │   ├── appraisal.py        # Performance reviews
│   │   ├── notifications.py    # In-app notifications
│   │   └── documents.py        # Document management
│   ├── static/
│   │   ├── index.html          # Static frontend
│   │   ├── career.html         # Public job listing
│   │   └── uploads/            # Resume & ICS files
│   └── Dockerfile              # Container image
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main router
│   │   ├── main.jsx            # React entry point
│   │   ├── api.js              # Axios HTTP client
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── JobAdmin.jsx
│   │   │   ├── Recruitment.jsx
│   │   │   ├── Applicants.jsx
│   │   │   ├── ApplicantDetail.jsx
│   │   │   ├── Pipeline.jsx
│   │   │   ├── Assessments.jsx
│   │   │   ├── OfferManagement.jsx
│   │   │   ├── BackgroundChecks.jsx
│   │   │   ├── Compliance.jsx
│   │   │   ├── Payslip.jsx
│   │   │   ├── Finance.jsx
│   │   │   ├── StaffDirectory.jsx
│   │   │   ├── LeaveManagement.jsx
│   │   │   ├── Timesheet.jsx
│   │   │   └── ... (more pages)
│   │   ├── components/
│   │   │   ├── DashboardLayout.jsx
│   │   │   └── PageHeader.jsx
│   │   └── contexts/
│   │       ├── AuthContext.jsx
│   │       └── NotificationContext.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── netlify.toml
│
├── docker-compose.yml
├── DEPLOYMENT.md
└── README.md (this file)
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ (for production) or SQLite (for development)

### Backend Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv-1
   source .venv-1/bin/activate  # On Windows: .venv-1\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Initialize database:**
   ```bash
   cd ..
   python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"
   ```

4. **Run the backend server:**
   ```bash
   uvicorn backend.main:app --reload
   ```

   Server runs on `http://localhost:8000`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

   App runs on `http://localhost:5173`

3. **Build for production:**
   ```bash
   npm run build
   ```

## Default Test Accounts

- **HR Admin**: `live_admin@peoplepluse.com` / `LiveAdmin123!`
- **Project Manager**: `live_manager@peoplepluse.com` / `LiveManager123!`
- **Staff**: `live_staff@peoplepluse.com` / `LiveStaff123!`

## API Documentation

FastAPI automatically generates interactive API docs at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

### Recruitment & ATS
- `POST /recruitment/jobs` - Create job posting
- `GET /recruitment/jobs` - List jobs
- `GET /recruitment/public/jobs` - Public job listing
- `POST /ats/applications/{app_id}/parse_resume` - Parse PDF/text resume
- `POST /ats/applications/{app_id}/invite` - Generate interview ICS invite
- `POST /ats/applications/{app_id}/advance` - Move application to next stage
- `GET /ats/pipeline` - Get pipeline by stage

### HR Tools
- `POST /hr/talent_pool` - Add to talent pool
- `POST /hr/referral` - Create referral
- `POST /hr/screen` - Screen application with keywords
- `POST /hr/offer/generate` - Generate offer
- `POST /hr/background/check` - Initiate background check
- `GET /hr/audit_log` - Compliance audit trail

### Payroll
- `POST /finance/payslips/generate` - Generate payslip
- `POST /upload/payslips_excel` - Import payslips from Excel
- `GET /finance/reports/summary` - Get financial summary
- `GET /finance/reports/csv` - Export as CSV

### Assessments
- `POST /assessments/templates` - Create assessment template
- `POST /assessments/submit` - Submit candidate assessment

## Configuration

### Environment Variables

Create a `.env` file in the backend directory (optional):

```env
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Database Setup for Production

For PostgreSQL, update `database.py`:

```python
DATABASE_URL = "postgresql://user:password@localhost/people_pluse_db"
```

## Features in Detail

### Resume Parsing

The system supports both PDF and text resume parsing:
- Extracts contact information (email, phone)
- Identifies candidate name
- Detects technical skills via keyword matching
- Stores parsed data for quick reference

To parse a resume:
```bash
POST /ats/applications/{app_id}/parse_resume
Content-Type: multipart/form-data
file: <PDF or text file>
```

### Interview Scheduling

Creates ICS calendar files for email invitations:
```bash
POST /ats/applications/{app_id}/invite
{
  "start_dt": "2026-06-20T14:00:00",
  "end_dt": "2026-06-20T15:00:00",
  "location": "Conference Room A",
  "summary": "Interview: John Doe",
  "panel": ["hr@company.com", "manager@company.com"]
}
```

### Payslip Generation

Excel import with automatic validation:
1. Upload Excel file with columns: EmployeeCode, GrossPay, Tax, Deductions
2. System matches employees and creates Payslip records
3. Generate PDF or export summary

### Compliance & Auditing

All HR actions are logged with:
- Timestamp
- User ID
- Action type
- Object affected
- Change details

Access via: `GET /hr/audit_log` (HR Admin only)

## Deployment

### Docker Deployment

```bash
docker-compose up
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Cloud Deployment Options

- **Frontend**: Netlify, Vercel, AWS S3 + CloudFront
- **Backend**: Render, AWS AppRunner, Google Cloud Run, Heroku
- **Database**: PostgreSQL on AWS RDS, Google Cloud SQL, Azure PostgreSQL

## Testing

Run backend syntax checks:
```bash
python -m py_compile backend/*.py backend/routers/*.py
```

Run frontend build:
```bash
cd frontend && npm run build
```

## Roadmap & Future Enhancements

- [ ] Real Google/Microsoft Calendar integration with OAuth
- [ ] Email notifications (SMTP integration)
- [ ] Mobile app (React Native)
- [ ] Video interviews (Zoom/Teams API)
- [ ] AI-powered resume screening
- [ ] Salary benchmarking & analytics
- [ ] Multi-language support (i18n)
- [ ] Advanced reporting dashboards
- [ ] Employee self-service portal
- [ ] Integration with ATS partners (LinkedIn, Workable)

## Troubleshooting

### Backend won't start
- Ensure Python 3.9+ is installed
- Check database URL in DATABASE_URL env var
- Run: `pip install -r requirements.txt` again

### Frontend build fails
- Clear npm cache: `npm cache clean --force`
- Delete node_modules: `rm -rf node_modules`
- Reinstall: `npm install`

### Resume parsing not working
- Ensure `pdfminer.six` is installed: `pip install pdfminer.six`
- Check file format (PDF or TXT)
- Check file size (< 50MB recommended)

## Support & Documentation

- API Docs: `http://localhost:8000/docs`
- Database Models: See `backend/models.py`
- Router Implementations: Check `backend/routers/`

## License

Proprietary - All rights reserved

## Contributors

- Development Team
- HR Consultants
- QA Team

---

**Last Updated**: June 2026  
**Version**: 1.0.0
