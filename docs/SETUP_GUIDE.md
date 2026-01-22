# Setup and Installation Guide

## Prerequisites

- Docker & Docker Compose (or)
- Python 3.9+ with pip
- Node.js 16+ with npm
- PostgreSQL 12+ (if not using Docker)
- Redis (if not using Docker)

## Quick Start with Docker

### 1. Clone the Repository
```bash
cd infra-analyzer-dashboard
```

### 2. Create Environment Files
```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

### 3. Configure Environment Variables
Edit `backend/.env`:
```
DATABASE_URL=postgresql://infra_user:infra_password@postgres:5432/infra_analyzer
WINRM_USERNAME=domain\username
WINRM_PASSWORD=your_password
FRONTEND_URL=http://localhost:3000
SECRET_KEY=your-secret-key
```

### 4. Start Services
```bash
docker-compose up -d
```

### 5. Access Applications
- **Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python -m app.db

# Run development server
python -m uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm start
```

## Database Setup

### Using Docker
Database is automatically initialized when services start.

### Manual PostgreSQL Setup
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE infra_analyzer;
CREATE USER infra_user WITH PASSWORD 'infra_password';
ALTER ROLE infra_user SET client_encoding TO 'utf8';
ALTER ROLE infra_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE infra_user SET default_transaction_deferrable TO on;
ALTER ROLE infra_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE infra_analyzer TO infra_user;

# Run migrations
python backend/app/db/init.py
```

## Configuration

### Windows Server Health Checks

Configure in `backend/.env`:
```
WINRM_PORT=5985
WINRM_SECURE_PORT=5986
WINRM_AUTH_METHOD=kerberos  # or ntlm, basic
```

Ensure WinRM is enabled on target servers:
```powershell
# Run as Administrator
Enable-PSRemoting -Force
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
Restart-Service WinRM
```

### Remote SSH Configuration

Place SSH private key at `backend/ssh_keys/id_rsa`:
```bash
mkdir -p backend/ssh_keys
cp /path/to/private/key backend/ssh_keys/id_rsa
chmod 600 backend/ssh_keys/id_rsa
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
pytest --cov=app tests/  # With coverage
```

### Frontend Tests
```bash
cd frontend
npm test
npm test -- --coverage  # With coverage
```

## Production Deployment

### Using Docker Compose
```bash
# Build images
docker-compose build

# Start in production mode
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Using Kubernetes
```bash
# Install Helm chart (if available)
helm install infra-analyzer ./k8s/helm-chart
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Reconnect
docker-compose down && docker-compose up -d
```

### API Connection Issues
```bash
# Check backend logs
docker-compose logs backend

# Test API
curl http://localhost:8000/health
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Clear Node cache
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

## Environment Variables Reference

### Backend (.env)
| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://localhost/infra_analyzer | Database connection string |
| REDIS_URL | redis://localhost:6379/0 | Redis cache URL |
| API_HOST | 0.0.0.0 | API listen host |
| API_PORT | 8000 | API listen port |
| SECRET_KEY | change-me | JWT secret key |
| FRONTEND_URL | http://localhost:3000 | Frontend URL for CORS |
| WINRM_USERNAME | domain\user | WinRM credentials |
| WINRM_PASSWORD | password | WinRM password |
| SMTP_SERVER | smtp.company.com | Email server |

### Frontend (.env)
| Variable | Default | Description |
|----------|---------|-------------|
| REACT_APP_API_BASE_URL | http://localhost:8000 | Backend API URL |
| REACT_APP_API_VERSION | v1 | API version |

## Support and Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Architecture Guide**: See `docs/ARCHITECTURE.md`
- **Capabilities**: See `docs/CAPABILITIES.md`
- **Health Check Logic**: See `docs/HEALTH_CHECK_LOGIC.md`

## Security Considerations

1. **Change default credentials** in production
2. **Use HTTPS** with valid SSL certificates
3. **Rotate JWT_SECRET** periodically
4. **Use strong database passwords**
5. **Enable WinRM authentication** (not basic auth)
6. **Use SSH keys** for remote authentication
7. **Set up VPN/firewall rules** for on-premise access
8. **Enable audit logging** for all operations

## Backup and Recovery

### Database Backup
```bash
docker-compose exec postgres pg_dump -U infra_user infra_analyzer > backup.sql
```

### Database Restore
```bash
docker-compose exec -T postgres psql -U infra_user infra_analyzer < backup.sql
```

## Performance Optimization

- Enable Redis caching
- Configure database connection pooling
- Use CDN for static assets
- Enable gzip compression
- Optimize database queries
- Use read replicas for reports

## Next Steps

1. Configure health check capabilities for your infrastructure
2. Set up server inventory
3. Create health check configurations
4. Schedule regular health checks
5. Configure email notifications
6. Set up monitoring and alerting
