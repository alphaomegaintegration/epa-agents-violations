# EPA Intelligent Compliance System - Production Deployment Guide

This guide covers deploying the EPA system to AWS EC2 or any production server with a real IP address or domain name.

## 🚀 Quick Deployment Summary

The system needs these changes for production:
1. Update CORS origins in backend
2. Update API URLs in frontend
3. Modify Docker Compose for production ports
4. Set up environment variables
5. Configure security groups (for AWS EC2)

## 📝 Required Code Changes

### 1. Backend CORS Configuration

**File**: `epa-demo/backend/main.py`

**Find this section** (around line 94):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Replace with**:
```python
import os

# Get allowed origins from environment variable
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Frontend API Configuration

**File**: `epa-demo/frontend/src/App.tsx`

**Find this section** (around line 7-8):
```typescript
const API_BASE = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';
```

**Replace with**:
```typescript
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
```

### 3. Production Docker Compose

**Create**: `epa-demo/docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"  # Serve on standard HTTP port
    environment:
      - REACT_APP_API_BASE=${REACT_APP_API_BASE}
      - REACT_APP_WS_URL=${REACT_APP_WS_URL}
    depends_on:
      - backend
    restart: unless-stopped

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"  # FastAPI backend
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - SERP_API_KEY=${SERP_API_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    volumes:
      - ./real_epa_violations_20250731_144819.json:/app/real_epa_violations_20250731_144819.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  epa_data:
```

### 4. Production Environment File

**Create**: `epa-demo/.env.prod`

```bash
# EPA Intelligent Compliance System - Production Environment

# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERP_API_KEY=your_serpapi_key_here

# Frontend Configuration (replace with your actual IP/domain)
REACT_APP_API_BASE=http://YOUR_EC2_IP:8000
REACT_APP_WS_URL=ws://YOUR_EC2_IP:8000/ws

# Backend CORS Configuration (replace with your actual IP/domain)
ALLOWED_ORIGINS=http://YOUR_EC2_IP,https://YOUR_DOMAIN.com,http://YOUR_EC2_IP:80

# Optional Configuration
EPA_API_TIMEOUT=30
MAX_VIOLATIONS_DISPLAY=10
```

## 🔧 Deployment Steps

### Step 1: Server Setup (AWS EC2)

1. **Launch EC2 Instance**:
   - Amazon Linux 2 or Ubuntu 20.04+
   - t3.medium or larger (system uses AI APIs)
   - Security Group with ports: 22, 80, 8000

2. **Install Docker and Docker Compose**:
```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Log out and back in for group changes
```

### Step 2: Deploy the Application

1. **Clone the repository**:
```bash
git clone https://github.com/alphaomegaintegration/epa-agents-violations.git
cd epa-agents-violations/epa-demo
```

2. **Set up production environment**:
```bash
cp .env.prod .env

# Edit with your actual values
nano .env

# Replace YOUR_EC2_IP with your actual EC2 public IP
# Replace YOUR_DOMAIN.com with your actual domain (if using one)
# Add your actual API keys
```

3. **Deploy with production configuration**:
```bash
docker-compose -f docker-compose.prod.yml --env-file .env up --build -d
```

### Step 3: Verify Deployment

1. **Check container status**:
```bash
docker-compose -f docker-compose.prod.yml ps
```

2. **Check logs**:
```bash
docker-compose -f docker-compose.prod.yml logs -f
```

3. **Test the application**:
   - Frontend: `http://YOUR_EC2_IP`
   - Backend API: `http://YOUR_EC2_IP:8000`
   - API Docs: `http://YOUR_EC2_IP:8000/docs`
   - Health Check: `http://YOUR_EC2_IP:8000/health`

## 🔒 AWS Security Group Configuration

**Inbound Rules**:
- **SSH (22)**: Your IP address only
- **HTTP (80)**: 0.0.0.0/0 (public access to frontend)
- **Custom TCP (8000)**: 0.0.0.0/0 (API access)
- **HTTPS (443)**: 0.0.0.0/0 (if using SSL)

## 🌐 Domain Setup (Optional)

If using a custom domain:

1. **Point domain to EC2 IP** (DNS A record)
2. **Update environment variables**:
```bash
REACT_APP_API_BASE=https://api.yourdomain.com
REACT_APP_WS_URL=wss://api.yourdomain.com/ws
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

3. **Set up SSL with Let's Encrypt** (recommended)

## 🔄 Updates and Maintenance

### Update the application:
```bash
cd epa-agents-violations
git pull origin main
cd epa-demo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d
```

### View logs:
```bash
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Monitor system:
```bash
docker stats
df -h  # Check disk space
htop   # Check CPU/memory usage
```

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**: Check `ALLOWED_ORIGINS` in `.env`
2. **API Connection Failed**: Verify `REACT_APP_API_BASE` URL
3. **WebSocket Connection Failed**: Check `REACT_APP_WS_URL`
4. **Container Won't Start**: Check `docker-compose logs`
5. **Out of Memory**: Upgrade to larger instance type

### Debug Commands:
```bash
# Check if containers are running
docker ps

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend

# Check environment variables
docker-compose -f docker-compose.prod.yml exec backend printenv

# Test API directly
curl http://YOUR_EC2_IP:8000/health
```

## 📊 Production URLs

After successful deployment:
- **Main Application**: `http://YOUR_EC2_IP`
- **API Documentation**: `http://YOUR_EC2_IP:8000/docs`
- **Available Systems**: `http://YOUR_EC2_IP:8000/systems`
- **Health Check**: `http://YOUR_EC2_IP:8000/health`

## 🔐 Security Notes

- Never commit API keys to the repository
- Use environment variables for all sensitive data
- Consider setting up HTTPS with SSL certificates
- Regularly update Docker images and dependencies
- Monitor API usage and costs
- Set up log rotation for Docker containers

---

**EPA Intelligent Compliance System** - Production deployment complete! 🏛️🚀