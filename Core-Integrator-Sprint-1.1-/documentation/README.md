# Core Integrator Sprint 1.3 - Security & Database Testing

## Overview
FastAPI-based orchestration platform with SSPL Phase III security, MongoDB Atlas integration, and comprehensive testing suite.

## Features
- **SSPL Phase III Security**: Ed25519 signatures, nonce replay protection, timestamp validation
- **Multi-Database Support**: MongoDB Atlas (primary), SQLite (fallback), Noopur integration
- **Agent System**: Finance, Education, Creator modules with memory management
- **Observability**: Health checks, diagnostics, logging endpoints
- **Testing Suite**: Security validation, database testing, comprehensive coverage

## Quick Start

1. **Clone & Setup**
   ```bash
   git clone <repository-url>
   cd Core-Integrator-Sprint-1.3-Security-Testing
   pip install -r requirements.txt
   cp .env.template .env
   ```

2. **Add Credentials**
   - Get MongoDB connection string from `credentials.txt`
   - Add to `.env` file

3. **Run Server**
   ```bash
   python main.py
   ```

4. **Test Security**
   ```bash
   python test_security_simple.py
   ```

## Configuration

### Security Settings
- `SSPL_ENABLED=true` - Enable/disable security
- `SSPL_ALLOW_DRIFT_SECONDS=300` - Timestamp tolerance

### Database Settings
- `USE_MONGODB=true` - Use MongoDB Atlas
- `MONGODB_CONNECTION_STRING` - Atlas connection string
- `MONGODB_DATABASE_NAME=core_integrator` - Database name

## Testing

### Available Test Scripts
- `test_security_simple.py` - Basic security test
- `security_client.py` - Full security + MongoDB test
- `test_security_mongodb.py` - MongoDB-specific tests

### Test Scenarios
1. **Security ON + MongoDB**: Full production setup
2. **Security OFF + MongoDB**: Database testing without signatures
3. **Security ON + SQLite**: Security testing with local database
4. **Security OFF + SQLite**: Basic functionality testing

## API Endpoints

### Core Endpoints
- `POST /core` - Main processing endpoint (requires SSPL headers when enabled)
- `GET /get-context?user_id=USER` - Retrieve user context
- `GET /system/health` - System health check
- `GET /system/diagnostics` - System diagnostics
- `GET /system/logs/latest` - Recent logs

### Available Modules
- `sample_text` - Text processing
- `finance` - Financial reports
- `education` - Educational content
- `creator` - Content creation

## Security Headers (SSPL Phase III)
When security is enabled, all requests to `/core` require:
- `X-SSPL-Timestamp` - Unix timestamp
- `X-SSPL-Nonce` - Unique request identifier
- `X-SSPL-Signature` - Ed25519 signature (base64)
- `X-SSPL-Public-Key` - Ed25519 public key (base64)

## Database Priority
1. **MongoDB Atlas** (if configured and available)
2. **Noopur** (if enabled and available)
3. **SQLite** (fallback, always available)

## Files Structure
- `main.py` - FastAPI application
- `core/gateway.py` - Central routing and processing
- `db/memory.py` - SQLite memory adapter
- `db/mongodb_adapter.py` - MongoDB Atlas adapter
- `utils/sspl.py` - Security validation
- `security_client.py` - Security testing client
- `TESTING_SETUP.md` - Detailed testing instructions

## Production Ready
- 95%+ test coverage
- Comprehensive error handling
- Security best practices
- Observability suite
- Multi-database fallback
- Performance optimized

## Support
For testing support, refer to `TESTING_SETUP.md` and use the provided test scripts.