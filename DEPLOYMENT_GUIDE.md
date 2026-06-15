# PEOPLE PLUSE HR Application - Deployment Guide

## Overview
People Plus is a comprehensive HR management system built with:
- **Backend**: FastAPI (Python) with SQLAlchemy ORM and SQLite database
- **Frontend**: React 18 + Vite with Material-UI components
- **Authentication**: JWT tokens with bearer token authorization
- **Database**: SQLite with 20+ models for complete HR functionality

---

## Application Features Implemented

### ✅ Core Modules
1. **Dashboard** - Main HR overview with staff metrics, contract monitoring, document tracking
2. **Staff Directory** - Employee profiles with document management and status tracking
3. **Leave Management** - Leave requests, approvals, balances, team leave calendar
4. **Timesheet** - Hour tracking, overtime calculation, approval workflows
5. **Payroll** - Payslip generation, salary management, payment tracking
6. **Performance Appraisals** - Employee ratings, feedback, performance tracking
7. **Recruitment** - Job postings, applications, candidate screening, offers, interviews
8. **Onboarding** - Automated checklists for new employees with task tracking
9. **Document Management** - Employee document upload, version control, missing documents tracking
10. **Contracts** - Automated contract generation from templates (appointment letters, offers, separation letters)

### ✅ Advanced Features
1. **Analytics & Reporting** - HR metrics, recruitment analytics, payroll trends, performance distribution
2. **Interview Scheduling** - Schedule and manage candidate interviews with interviewer assignment
3. **Contract Alerts** - Automatic notifications for contracts expiring in 30/60/90 days
4. **Compliance & Audit** - Full audit logging, compliance tracking, data export capabilities
5. **Role-Based Access Control** - Route guards enforcing hr_admin, project_manager, staff, finance roles
6. **Notifications** - In-app notifications with read/unread tracking
7. **Internship Management** - Intern tracking with mentorship assignment

---

## Deployment Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- SQLite 3

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Initialize Database
```bash
# Database will auto-initialize on first run via main.py
# Seed data includes test users:
# - live_admin@peoplepluse.com / admin123 (hr_admin)
# - live_manager@peoplepluse.com / manager123 (project_manager)
# - live_staff@peoplepluse.com / staff123 (staff)
# - finance@peoplepluse.com / finance123 (finance)
```

#### 3. Run Backend Server
```bash
# Option 1: Direct Python
python backend/main.py

# Option 2: Uvicorn
uvicorn backend.main:app --reload --port 8000

# Option 3: Docker
docker build -f backend/Dockerfile -t people-pluse-backend .
docker run -p 8000:8000 people-pluse-backend
```

Backend runs on: http://localhost:8000
API docs available at: http://localhost:8000/docs

### Frontend Setup

#### 1. Install Dependencies
```bash
cd frontend
npm install
```

#### 2. Configure API Endpoint
Update `frontend/src/api.js` if needed:
```javascript
// Default points to http://localhost:8000
// Update for production: https://your-production-api.com
```

#### 3. Run Development Server
```bash
npm run dev
```
Frontend runs on: http://localhost:5173

#### 4. Build for Production
```bash
npm run build
# Output in: frontend/dist/
# Deploy dist/ folder to your hosting
```

---

## Environment Configuration

### Backend (.env or environment variables)
```
DATABASE_URL=sqlite:///./people_pluse.db
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
UPLOAD_DIR=./uploads
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

---

## API Endpoints Summary

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Current user profile

### Employees
- `GET /employees/` - List all employees
- `POST /employees/` - Create new employee
- `GET /employees/{id}` - Get employee details
- `PUT /employees/{id}` - Update employee

### Leave
- `POST /api/leave/request` - Submit leave request
- `GET /api/leave/requests` - List leave requests
- `GET /api/leave/balance/{emp_id}` - Get leave balance
- `GET /api/leave/calendar/{project}` - Team leave calendar
- `PUT /api/leave/approve/{request_id}` - Approve leave
- `PUT /api/leave/reject/{request_id}` - Reject leave

### Payroll
- `POST /finance/payslips/generate` - Generate payslip
- `GET /finance/payslips` - List payslips
- `GET /finance/reports/payslips_csv` - Export payslips

### Reporting
- `GET /reporting/hr_metrics` - HR analytics
- `GET /reporting/recruitment_metrics` - Recruitment metrics
- `GET /reporting/payroll_metrics` - Payroll analytics
- `GET /reporting/timesheet_metrics` - Timesheet analytics
- `GET /reporting/export_dashboard_summary` - All metrics

### Documents
- `POST /documents/generate` - Generate contract/letter
- `GET /documents/templates` - Available templates

### HR Tools
- `GET /hr/onboarding` - List checklists
- `PUT /hr/onboarding/{id}` - Update checklist
- `POST /hr/alerts/scan_contracts` - Scan contract expiry

---

## Frontend Routes & Access Control

| Route | Allowed Roles | Component |
|-------|---|-----------|
| `/` | All | Dashboard |
| `/staff` | hr_admin, project_manager, staff, finance | Staff Directory |
| `/recruitment` | hr_admin, project_manager | Recruitment |
| `/recruitment-admin` | hr_admin, project_manager | Job Admin |
| `/applicants` | hr_admin, project_manager | Applicants |
| `/pipeline` | hr_admin, project_manager | Pipeline |
| `/finance` | hr_admin, project_manager, finance | Finance |
| `/payslips` | hr_admin, project_manager, staff, finance | Payslips |
| `/leave` | hr_admin, project_manager, staff | Leave Management |
| `/timesheet` | hr_admin, project_manager, staff | Timesheet |
| `/appraisals` | hr_admin, project_manager, staff | Appraisals |
| `/reporting` | hr_admin, project_manager | Analytics |
| `/onboarding` | hr_admin, project_manager | Onboarding |
| `/contracts` | hr_admin, project_manager | Contract Generation |
| `/interviews` | hr_admin, project_manager | Interview Scheduling |
| `/compliance` | hr_admin, project_manager | Compliance & Audit |

---

## Database Schema

### Core Models
- `User` - System users with roles
- `Employee` - Staff records with personal/employment details
- `LeaveRequest` - Leave applications with approval workflow
- `Timesheet` - Hours worked tracking
- `Payslip` - Salary records
- `PerformanceAppraisal` - Employee ratings
- `Application` - Job applications
- `Interview` - Interview records
- `Offer` - Job offers
- `OnboardingChecklist` - New hire onboarding tasks
- `Notification` - System notifications
- `AuditLog` - Activity tracking

### File Uploads
Uploaded files stored in: `./uploads/{employee_id}/`

---

## Testing

### Backend Unit Tests
```bash
# Run syntax checks
python -m py_compile backend/routers/*.py

# Run pytest if tests exist
pytest backend/tests/
```

### Frontend Components
```bash
# Run Vite server for testing
npm run dev

# Build and preview
npm run build
npm run preview
```

### Manual Testing Checklist
- [ ] Login with each role (hr_admin, project_manager, staff, finance)
- [ ] Verify role-based navigation appears correctly
- [ ] Test leave request submission and approval
- [ ] Generate payslips and verify calculations
- [ ] Create recruitment records and advance pipeline
- [ ] Upload employee documents
- [ ] Generate contracts from templates
- [ ] Schedule interviews
- [ ] Check analytics dashboard metrics
- [ ] Verify onboarding checklist functionality

---

## Troubleshooting

### Backend Issues
1. **Database lock error**
   ```bash
   # Delete database and reinitialize
   rm people_pluse.db
   python backend/main.py
   ```

2. **Port 8000 already in use**
   ```bash
   # Run on different port
   uvicorn backend.main:app --port 8001
   ```

3. **Import errors**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r backend/requirements.txt
   ```

### Frontend Issues
1. **CORS errors**
   - Check backend CORS configuration in `main.py`
   - Verify API URL in `frontend/src/api.js`

2. **JWT token expired**
   - Clear localStorage and re-login
   - Check token expiration in backend auth config

3. **Build errors**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

---

## Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access:
# Backend: http://localhost:8000
# Frontend: http://localhost:80
```

### Cloud Deployment (Heroku/Render)
1. Push code to Git repository
2. Configure environment variables
3. Deploy backend to API platform
4. Deploy frontend to static hosting (Netlify/Vercel)
5. Update frontend API URL for production

### Security Checklist
- [ ] Change default JWT secret key
- [ ] Enable HTTPS/SSL in production
- [ ] Configure proper CORS origins
- [ ] Set database backups schedule
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Use strong password requirements
- [ ] Enable 2FA (optional)

---

## Performance Optimization

1. **Database Indexing** - Add indexes on frequently queried columns
2. **Caching** - Implement Redis for session/notification caching
3. **Pagination** - Limit API responses to 50-100 records per page
4. **Frontend Optimization**:
   - Code splitting by route
   - Lazy loading of components
   - Image optimization
   - Minification for production build

---

## Support & Maintenance

### Monitoring
- Check application logs regularly
- Monitor database size and perform cleanup
- Review audit logs for security issues

### Backups
```bash
# Backup database
cp people_pluse.db people_pluse.db.backup

# Backup uploads
tar -czf uploads_backup.tar.gz uploads/
```

### Updates
- Keep dependencies updated: `pip list --outdated` and `npm outdated`
- Review security patches monthly
- Test updates in staging before production

---

## Key Technologies & Versions

- Python 3.8+
- FastAPI 0.95+
- SQLAlchemy 2.0+
- React 18.2+
- Material-UI 5.12+
- Vite 4.0+
- Axios 1.4+

---

## Contact & Support

For issues or questions:
1. Check application logs
2. Review API documentation at `/docs`
3. Contact development team

---

**Last Updated:** January 2024
**Version:** 1.0.0 - MVP Release
