# Core Integrator Deployment Guide

## Overview
The Core Integrator is a FastAPI service that orchestrates requests between Finance, Education, and Creator agents. This guide covers local development and Docker deployment for demo environments.

## Prerequisites
- Python 3.11+
- Docker (for containerized deployment)
- Git

## Local Development

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd core-integrator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your configuration values.

### Required Environment Variables
- `DB_PATH`: Path to SQLite database file (default: `data/context.db`)
- `INTEGRATOR_USE_NOOPUR`: Enable Noopur integration (`true`/`false`, default: `false`)
- `NOOPUR_BASE_URL`: Noopur service URL (required if `INTEGRATOR_USE_NOOPUR=true`)
- `NOOPUR_API_KEY`: API key for Noopur (required if `INTEGRATOR_USE_NOOPUR=true`)
- `VIDEO_SERVICE_URL`: Video generation service URL (required)
- `VIDEO_SERVICE_TIMEOUT`: Timeout for video service calls in seconds (default: `300`)
- `USE_MONGODB`: Use MongoDB instead of SQLite (`true`/`false`, default: `false`)
- `MONGODB_CONNECTION_STRING`: MongoDB connection string (required if `USE_MONGODB=true`)
- `MONGODB_DATABASE_NAME`: MongoDB database name (default: `core_integrator`)
- `SSPL_ENABLED`: Enable SSPL security validation (`true`/`false`, default: `false`)
- `SSPL_ALLOW_DRIFT_SECONDS`: Allowed timestamp drift for SSPL (default: `300`)
- `LOG_LEVEL`: Logging level (`INFO`, `DEBUG`, etc., default: `INFO`)

### Optional Environment Variables
- `NONCE_DB_PATH`: Path to nonce store database (default: `db/nonce_store.db`)
- `CREATORCORE_BASE_URL`: CreatorCore service URL (default: `http://localhost:5002`)
- `CREATORCORE_API_KEY`: API key for CreatorCore
- `FLASK_ENV`: Environment mode (default: `development`)
- `FLASK_DEBUG`: Enable debug mode (`true`/`false`, default: `false`)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: `30`)
- `MAX_RETRIES`: Maximum retry attempts (default: `3`)
- `CONNECTION_POOL_SIZE`: Connection pool size (default: `10`)

### Running Locally
```bash
python main.py
```

The service will start on `http://localhost:8001`

### Health Check
```bash
curl http://localhost:8001/system/health
```

Expected response:
```json
{
  "status": "ok",
  "dependencies": {
    "database": "up",
    "gateway": "up",
    "noopur": "disabled",
    "video_service": "up"
  },
  "timestamp": "2024-01-27T10:00:00Z"
}
```

## Docker Deployment

### Build the Image
```bash
docker build -t core-integrator .
```

### Run with Docker
```bash
docker run -p 8001:8001 \
  -e DB_PATH=data/context.db \
  -e INTEGRATOR_USE_NOOPUR=false \
  -e VIDEO_SERVICE_URL=http://host.docker.internal:5002 \
  core-integrator
```

### Run with Docker Compose (Multi-Service)
For full demo setup with dependent services:
```bash
docker-compose up
```

## Health & Diagnostics

### Health Endpoint (`/system/health`)
Returns binary status (`ok`/`down`) and explicit dependency status:
- `database`: SQLite connection status
- `gateway`: Core gateway initialization
- `noopur`: Noopur service connectivity (if enabled)
- `video_service`: Video generation service status

### Diagnostics Endpoint (`/system/diagnostics`)
Internal monitoring details (not for production exposure):
- Configuration summary
- Database latency measurements
- Agent/module loading status
- Feature flag states

## Monitoring & Logging

The service uses structured JSON logging compatible with external telemetry systems. Logs include:
- Dependency call latency
- Error classification (network, schema, logic, unexpected)
- Request/response metadata
- User IDs (sanitized)

## Troubleshooting

### Common Issues

1. **Configuration Validation Errors**
   - Check that all required environment variables are set
   - Verify `.env` file is properly formatted

2. **Database Connection Issues**
   - Ensure `data/` directory exists and is writable
   - Check SQLite file permissions

3. **External Service Timeouts**
   - Verify dependent services are running
   - Check network connectivity
   - Review timeout configurations

4. **Health Check Failures**
   - Use `/system/diagnostics` for detailed status
   - Check service logs for error details

### Log Analysis
```bash
# View recent logs
curl http://localhost:8001/system/logs/latest

# Structured JSON logs are output to stdout/stderr
# Pipe to jq for formatting: docker logs <container> | jq
```

## Demo Configuration

For live demos, use these minimal settings:
```env
DB_PATH=data/context.db
INTEGRATOR_USE_NOOPUR=false
VIDEO_SERVICE_URL=http://localhost:5002
LOG_LEVEL=INFO
SSPL_ENABLED=false
```

This disables external dependencies and focuses on core functionality.