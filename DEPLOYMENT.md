# Deployment Guide

This document describes deployment strategies for ops-monitor monorepo containing two applications: **Central** (dashboard) and **Agent** (monitoring agent).

## Overview

- **Central**: Deployed on one central server, collects and displays metrics from all agents
- **Agent**: Deployed on multiple VMs, collects system metrics and exposes them via API

## Deployment Options

### Option 1: Sparse Checkout (Development/Testing)

Best for: Development, testing, quick deployments

This method uses Git's sparse checkout to clone only the necessary parts of the repository.

#### Agent Deployment

```bash
# Clone repository with sparse checkout
git clone --sparse --filter=blob:none <repository-url> ops-monitor
cd ops-monitor

# Checkout only agent and shared code
git sparse-checkout set agent shared

# Setup and run
cd agent
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your configuration

# Run
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Central Deployment

```bash
# Clone repository with sparse checkout
git clone --sparse --filter=blob:none <repository-url> ops-monitor
cd ops-monitor

# Checkout only central and shared code
git sparse-checkout set central shared

# Setup and run
cd central
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your configuration

# Run
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Updates

```bash
cd ops-monitor
git pull
cd agent  # or central
pip install -r requirements.txt
# Restart the application
```

**Pros:**
- Simple Git workflow
- Easy updates with `git pull`
- No additional infrastructure needed
- Good for development and testing

**Cons:**
- Requires Git on production servers
- Requires Python environment setup on each VM
- Less isolated than containers
- Manual dependency management

---

### Option 2: Docker Images (Production) - RECOMMENDED

Best for: Production deployments, scalability, consistency

This method builds separate Docker images for each application from the monorepo.

#### Prerequisites

- Docker and Docker Compose installed on target VMs
- Docker Registry access (GitHub Container Registry, Docker Hub, or private registry)

#### Repository Structure

```
ops-monitor/
├── agent/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── ...
├── central/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── ...
├── shared/
└── .github/workflows/
    ├── build-agent.yml
    └── build-central.yml
```

#### Building Images

**Locally:**

```bash
# From repository root

# Build Agent image
docker build -f agent/Dockerfile -t ops-monitor-agent:latest .

# Build Central image
docker build -f central/Dockerfile -t ops-monitor-central:latest .

# Push to registry (if needed)
docker tag ops-monitor-agent:latest ghcr.io/yourusername/ops-monitor-agent:latest
docker push ghcr.io/yourusername/ops-monitor-agent:latest

docker tag ops-monitor-central:latest ghcr.io/yourusername/ops-monitor-central:latest
docker push ghcr.io/yourusername/ops-monitor-central:latest
```

**With CI/CD (GitHub Actions):**

Images are automatically built and pushed to GitHub Container Registry on push to main branch.

#### Agent Deployment

On each VM where you want to run the agent:

```bash
# Create deployment directory
mkdir -p ~/ops-monitor-agent
cd ~/ops-monitor-agent

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/yourusername/ops-monitor/main/agent/docker-compose.yml

# Create .env file
cat > .env << EOF
PROJECT_NAME=ops-monitor-agent
ENVIRONMENT=production
CENTRAL_URL=https://central.example.com
AGENT_PORT=8000
# Add other configuration
EOF

# Pull and start
docker-compose pull
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Central Deployment

On the central server:

```bash
# Create deployment directory
mkdir -p ~/ops-monitor-central
cd ~/ops-monitor-central

# Download docker-compose.yml
curl -O https://raw.githubusercontent.com/yourusername/ops-monitor/main/central/docker-compose.yml

# Create .env file
cat > .env << EOF
PROJECT_NAME=ops-monitor-central
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@db:5432/opsmonitor
SECRET_KEY=your-secret-key-here
CENTRAL_PORT=8000
# Add other configuration
EOF

# Pull and start
docker-compose pull
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Updates

```bash
cd ~/ops-monitor-agent  # or ~/ops-monitor-central

# Pull latest image
docker-compose pull

# Recreate containers with new image
docker-compose up -d

# Clean old images
docker image prune -f
```

**Pros:**
- Clean separation - only Docker images on production
- No Git or Python environment needed on VMs
- Consistent environment across all deployments
- Easy rollbacks (tag-based versioning)
- Standard CI/CD workflow
- Better isolation and security

**Cons:**
- Requires Docker Registry
- Slightly more complex initial setup
- Need to manage image versions/tags

---

## Comparison

| Feature | Sparse Checkout | Docker Images |
|---------|----------------|---------------|
| Setup Complexity | Low | Medium |
| Production Ready | Testing/Dev | Yes |
| Requires Git | Yes | No |
| Requires Python Setup | Yes | No |
| Rollback Easy | No | Yes |
| CI/CD Integration | Manual | Native |
| Isolation | None | Full |
| Updates | `git pull` | `docker-compose pull` |
| Best For | Development, Testing | Production |

---

## Recommended Workflow

1. **Development**: Use Sparse Checkout (Option 1) for local testing
2. **Staging**: Use Docker Images (Option 2) to test containerized deployment
3. **Production**: Use Docker Images (Option 2) with proper CI/CD pipeline

---

## Environment Configuration

Both applications require `.env` files for configuration.

### Agent .env Example

```env
PROJECT_NAME=ops-monitor-agent
ENVIRONMENT=production
AGENT_PORT=8000
CENTRAL_URL=https://central.example.com
LOG_LEVEL=INFO
METRICS_COLLECTION_INTERVAL=60
```

### Central .env Example

```env
PROJECT_NAME=ops-monitor-central
ENVIRONMENT=production
CENTRAL_PORT=8000
DATABASE_URL=postgresql://user:pass@localhost:5432/opsmonitor
SECRET_KEY=your-very-secret-key-change-in-production
LOG_LEVEL=INFO
CORS_ORIGINS=["https://dashboard.example.com"]
```

---

## Security Considerations

1. **Never commit `.env` files** - they are in `.gitignore`
2. **Use strong SECRET_KEY** in production
3. **Use HTTPS** for communication between Agent and Central
4. **Implement authentication** for Agent API endpoints
5. **Keep Docker images updated** with security patches
6. **Use Docker secrets** for sensitive data in production
7. **Restrict network access** - only Central should access Agent APIs

---

## Monitoring & Maintenance

### Health Checks

Both applications expose health check endpoints:

```bash
# Agent
curl http://localhost:8000/health

# Central
curl http://localhost:8000/health
```

### Logs

**Sparse Checkout:**
```bash
# Application logs in logs/ directory or stdout
tail -f logs/app.log
```

**Docker:**
```bash
docker-compose logs -f
docker-compose logs -f agent  # specific service
```

### Backup

**Central Database Backup:**
```bash
# PostgreSQL backup
docker-compose exec db pg_dump -U user opsmonitor > backup.sql

# Restore
docker-compose exec -T db psql -U user opsmonitor < backup.sql
```

---

## Troubleshooting

### Sparse Checkout: Can't see files after clone

```bash
git sparse-checkout list  # Check what's checked out
git sparse-checkout set agent shared  # Reset checkout
```

### Docker: Container won't start

```bash
docker-compose logs  # Check logs
docker-compose down && docker-compose up -d  # Restart
```

### Docker: Port already in use

```bash
# Change port in .env or docker-compose.yml
AGENT_PORT=8001  # Use different port
```

### Docker: Image pull fails

```bash
# Login to registry
docker login ghcr.io -u username

# Check image name and tag
docker images | grep ops-monitor
```

---

## CI/CD Pipeline (GitHub Actions)

Example workflow for building and pushing images:

**.github/workflows/build-agent.yml**

```yaml
name: Build Agent Image

on:
  push:
    branches: [main, develop]
    paths:
      - 'agent/**'
      - 'shared/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: .
          file: agent/Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/agent:latest
            ghcr.io/${{ github.repository }}/agent:${{ github.sha }}
```

Similar workflow for Central application.

---

## Support

For issues and questions, please refer to the main [README.md](README.md) or create an issue in the repository.
