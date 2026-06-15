# PEOPLE PLUSE - Comprehensive Deployment Guide

Complete guide for deploying PEOPLE PLUSE to production environments.

## Quick Start: Docker Compose

### Local/Staging

```bash
# Build and start all services
docker-compose up --build

# Application available at http://localhost:8000
# Frontend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

The Docker setup handles:
- Frontend build (React → static files in backend/static)
- Backend dependencies installation
- Database initialization
- Uvicorn server on port 8000

## Production Deployments

### Option 1: Render.com (Recommended - Free tier available)

#### Backend (Web Service)

1. Connect GitHub repository to Render
2. Create new Web Service:
   - **Name**: people-pluse-api
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn backend.main:app --workers 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

3. Environment Variables:
   ```
   DATABASE_URL=<postgresql connection string>
   SECRET_KEY=<generate-random-key>
   FRONTEND_URL=https://people-pluse-frontend.netlify.app
   ```

4. Create PostgreSQL database on Render (linked to Web Service)

#### Frontend (Static Site)

1. Create Render Static Site:
   - **Name**: people-pluse-frontend
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

2. Configure environment variable:
   ```
   VITE_API_URL=https://people-pluse-api.onrender.com
   ```

### Option 2: AWS Deployment

#### Backend (AppRunner)

1. Build Docker image:
   ```bash
   aws ecr get-login-password | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
   docker build -t people-pluse-api:latest .
   docker tag people-pluse-api:latest <account-id>.dkr.ecr.<region>.amazonaws.com/people-pluse-api:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/people-pluse-api:latest
   ```

2. Create AppRunner service from ECR image
3. Configure environment variables in AppRunner console
4. Set up RDS PostgreSQL database

#### Frontend (S3 + CloudFront)

1. Build and upload:
   ```bash
   cd frontend && npm run build
   aws s3 sync dist s3://people-pluse-frontend-bucket
   ```

2. Create CloudFront distribution:
   - Origin: S3 bucket
   - Alternate domain: your domain
   - SSL: ACM certificate

#### Database (RDS)

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier people-pluse-db \
  --engine postgres \
  --db-instance-class db.t3.micro \
  --master-username admin \
  --master-user-password <secure-password>

# Get endpoint and update DATABASE_URL
```

### Option 3: Heroku Deployment

```bash
# Install Heroku CLI
curl https://cli.heroku.com/install.sh | sh

# Create app
heroku create people-pluse-api

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FRONTEND_URL=https://people-pluse-frontend.netlify.app

# Deploy
git push heroku main

# Check logs
heroku logs --tail
```

## Environment Configuration

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/people_pluse

# Security
SECRET_KEY=your-very-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Frontend
FRONTEND_URL=https://yourdomain.com

# Optional: Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password

# Optional: AWS S3 for file storage
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=people-pluse-uploads

# Optional: Calendar integration
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
```

### Frontend (.env.production)

```env
VITE_API_URL=https://api.yourdomain.com
```

## Database Setup

### Initialize PostgreSQL

```bash
# Create database
createdb people_pluse_db

# Create user
createuser people_pluse_user
psql -c "ALTER USER people_pluse_user WITH PASSWORD 'secure-password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE people_pluse_db TO people_pluse_user;"

# Initialize schema
python -c "from backend.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Verify
psql -U people_pluse_user -d people_pluse_db -c "SELECT * FROM users LIMIT 1;"
```

### Backup Database

```bash
# Full backup
pg_dump people_pluse_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Compress for storage
gzip backup_*.sql

# Restore from backup
psql people_pluse_db < backup.sql
```

## SSL/HTTPS Setup

### Let's Encrypt (Free)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com
sudo certbot renew --dry-run  # Auto-renews every 90 days
```

### CloudFlare (Recommended)

1. Add domain to CloudFlare
2. Update nameservers at registrar
3. Enable "Full (strict)" SSL
4. Configure firewall rules as needed

## Performance Optimization

### Backend

```bash
# Use multiple workers
gunicorn backend.main:app --workers 4 -k uvicorn.workers.UvicornWorker

# Enable gzip compression
# Configure in Nginx:
add_header Content-Encoding gzip;
```

### Frontend

```bash
# Production build (minified, optimized)
cd frontend && npm run build

# Serve with compression
# Enable gzip in web server
```

### Database

```bash
# Vacuum and analyze (PostgreSQL)
VACUUM ANALYZE;

# Index key queries (already done in models.py)
CREATE INDEX idx_applications_status ON applications(status);
```

## Monitoring & Logging

### Application Health

```bash
# Health check endpoint
GET /api/health
```

### Error Tracking (Sentry)

```bash
pip install sentry-sdk
```

Add to `backend/main.py`:
```python
import sentry_sdk
sentry_sdk.init("your-sentry-dsn")
```

### Logs

- **Development**: Check `docker-compose logs`
- **Production**: Use CloudWatch (AWS), Stackdriver (GCP), or Cloud Logging (Azure)

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS configured (only frontend domain)
- [ ] Rate limiting enabled
- [ ] Secrets in environment variables (not code)
- [ ] Dependencies updated: `pip list --outdated` and `npm outdated`
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] XSS prevention (React escapes)
- [ ] CSRF tokens (if needed)
- [ ] Audit logging enabled
- [ ] Backups automated and tested

## Scaling

### Horizontal

- Multiple backend instances behind load balancer (AWS ELB, Render)
- Database read replicas for reporting
- Static file storage in S3/CloudStorage
- Redis cache for sessions

### Vertical

- Increase server RAM/CPU
- Upgrade database tier
- Use database connection pooling (PgBouncer)

## Backup & Recovery

```bash
# Daily automated backups (cron job)
0 2 * * * pg_dump $DATABASE_URL | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz

# Upload to S3
0 3 * * * aws s3 cp /backups/db_$(date +\%Y\%m\%d).sql.gz s3://backup-bucket/daily/

# Keep 30 days
0 4 * * * find /backups -type f -mtime +30 -delete
```

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Requires 3.9+

# Check dependencies
pip install -r requirements.txt

# Test database connection
psql $DATABASE_URL -c "SELECT 1"
```

### Resume parsing fails

```bash
# Ensure pdfminer.six installed
pip install pdfminer.six

# Test PDF processing
python -c "from pdfminer.high_level import extract_text; print(extract_text('test.pdf'))"
```

### Frontend build fails

```bash
# Clear cache
npm cache clean --force
rm -rf node_modules
npm install
npm run build
```

## Cost Estimation (Monthly, US Regions)

| Component | Service | Size | Cost |
|-----------|---------|------|------|
| Backend | Render | Medium | $12 |
| Database | RDS | db.t3.micro | $15 |
| Frontend | Netlify/S3 | Free tier | $0 |
| Storage | S3 | 10GB | $0.23 |
| CDN | CloudFlare | Free | $0 |
| **Total** | | | **~$27** |

---

**Last Updated**: June 2026
**Version**: 1.0.0
