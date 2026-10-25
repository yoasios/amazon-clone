# Docker Operations Guide

## Architecture Overview

This is a **single-container FastAPI application** with:
- Backend: FastAPI with async SQLAlchemy
- Frontend: Static HTML/CSS/JavaScript served by FastAPI
- Database: PostgreSQL (production) or SQLite (development)
- No microservices, workers, or external queues

## Quick Start

### Production Mode

```bash
# Build and start the stack
docker compose up -d

# View logs
docker compose logs -f app

# Stop the stack
docker compose down

# Stop and remove volumes (deletes database)
docker compose down -v
```

### Development Mode

```bash
# Start with hot reload and source code mounting
docker compose -f compose.yaml -f compose.dev.yaml up

# Build without cache
docker compose build --no-cache

# Rebuild after dependency changes
docker compose build
```

## Environment Configuration

Create a `.env` file in the project root:

```bash
# PostgreSQL (production)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=amazon_db

# JWT Secrets (generate secure random strings)
JWT_SECRET=your_jwt_secret_min_32_chars
SHOP_COOKIE_SECRET=your_shop_cookie_secret_min_32_chars
```

**Do not commit `.env` to version control.** Use `.env.example` as a template.

## Commands Reference

### Building Images

```bash
# Build production image
docker compose build

# Build development image
docker compose -f compose.yaml -f compose.dev.yaml build

# Build without cache
docker compose build --no-cache

# Build specific service
docker compose build app
```

### Running Containers

```bash
# Start in detached mode
docker compose up -d

# Start with logs
docker compose up

# Start development mode
docker compose -f compose.yaml -f compose.dev.yaml up

# Restart containers
docker compose restart

# Restart specific service
docker compose restart app
```

### Viewing Logs

```bash
# Follow logs for all services
docker compose logs -f

# Follow logs for app only
docker compose logs -f app

# View last 100 lines
docker compose logs --tail=100 app

# View logs since specific time
docker compose logs --since 1h app
```

### Health Checks

```bash
# Check health status
docker compose ps

# Check container health
docker inspect amazon_app | grep -A 10 Health

# Manual health check
curl http://localhost:8000/health
```

### Executing Commands

```bash
# Open shell in app container
docker compose exec app bash

# Run Python command
docker compose exec app python -c "print('Hello')"

# Check Python version
docker compose exec app python --version

# List installed packages
docker compose exec app pip list
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U postgres -d amazon_db

# Backup database
docker compose exec postgres pg_dump -U postgres amazon_db > backup.sql

# Restore database
docker compose exec -T postgres psql -U postgres amazon_db < backup.sql

# View PostgreSQL logs
docker compose logs postgres
```

### Stopping and Cleanup

```bash
# Stop containers
docker compose stop

# Stop and remove containers
docker compose down

# Stop and remove containers and volumes (deletes data)
docker compose down -v

# Remove all images
docker compose down --rmi all

# Remove unused images
docker image prune -a
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs app

# Check if port 8000 is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Rebuild image
docker compose build --no-cache
```

### Database Connection Issues

```bash
# Check PostgreSQL health
docker compose ps postgres

# Verify PostgreSQL is ready
docker compose exec postgres pg_isready -U postgres

# Check DATABASE_URL in .env
docker compose exec app env | grep DATABASE_URL
```

### Permission Issues

```bash
# Fix file permissions if needed
docker compose exec app chown -R appuser:appuser /app
```

### Health Check Failing

```bash
# Manual health check
docker compose exec app python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Check if app is running
docker compose exec app ps aux

# Check port binding
docker compose exec app netstat -tlnp
```

## Deployment Considerations

### Production Checklist

- [ ] Set strong PostgreSQL password
- [ ] Generate secure JWT secrets (32+ characters)
- [ ] Remove development mode port exposure from compose.yaml
- [ ] Set up PostgreSQL backups
- [ ] Configure reverse proxy (nginx) for SSL
- [ ] Set resource limits in compose.yaml
- [ ] Configure logging aggregation
- [ ] Set up monitoring and alerting
- [ ] Use managed PostgreSQL service for production
- [ ] Use container registry for image storage

### Resource Limits (Optional)

Add to `compose.yaml`:

```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
  postgres:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### Scaling

```bash
# Scale app horizontally (requires stateless design)
docker compose up -d --scale app=3

# Note: PostgreSQL is not scalable this way
# Use managed PostgreSQL for production scaling
```

## Security Notes

- **Rootless containers**: App runs as non-root user `appuser`
- **No secrets in image**: All secrets injected via environment variables
- **Minimal base image**: Python 3.14-slim (reduced attack surface)
- **Database isolation**: PostgreSQL in separate container
- **No exposed database port**: PostgreSQL not accessible from host in production
- **Read-only filesystem**: Consider adding `read_only: true` for app service

## Backup and Restore

### Backup

```bash
# Backup PostgreSQL volume
docker run --rm -v amazon_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Backup entire application state
docker compose exec postgres pg_dump -U postgres amazon_db > backup.sql
```

### Restore

```bash
# Restore PostgreSQL
docker exec -i amazon_postgres psql -U postgres amazon_db < backup.sql

# Restore from volume backup
docker run --rm -v amazon_postgres_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build image
        run: docker compose build
      - name: Run tests
        run: docker compose run app pytest
      - name: Push to registry
        run: docker push your-registry/amazon:latest
```

## Additional Resources

- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Docker Compose Best Practices](https://docs.docker.com/compose/compose-file/compose-file-v3/)
