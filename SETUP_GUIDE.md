# Setup Guide - Core Integrator & Creator Core Integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### 1. Start Core Integrator
```bash
cd Core-Integrator-Sprint-1.1-
pip install -r requirements.txt
python main.py
```
**Service runs on:** http://localhost:8000

### 2. Start Creator Core
```bash
cd creator-core
pip install -r requirements.txt
python app.py
```
**Service runs on:** http://localhost:5002

### 3. Use Integration Layer
```python
# Example usage
from integration.creator_client import CreatorClient
from integration.health_checks import HealthChecker

# Create client
client = CreatorClient()
result = client.generate("Test prompt")

# Check health
health = HealthChecker()
status = health.aggregate_health()
```

## 🔧 Integration Components

### creator_client.py
HTTP client for Creator Core API calls
- `/generate` - Content generation
- `/feedback` - Submit feedback  
- `/history` - Get generation history

### core_bridge.py
Connects Core Integrator with Creator Core
- Forwards creator requests
- Handles feedback routing
- Maintains data integrity

### health_checks.py
Aggregates health status from both services
- Core Integrator health via `/system/health`
- Creator Core health via `/history`
- Combined status reporting

### config_reader.py
Reads existing configuration files
- Core Integrator `.env` file
- Creator Core settings
- Service URL discovery

## 🧪 Testing Integration

### Health Check
```python
from integration.health_checks import HealthChecker
health = HealthChecker()
print(health.aggregate_health())
```

### Generate Content
```python
from integration.creator_client import CreatorClient
client = CreatorClient()
result = client.generate("Write a story about AI")
print(result)
```

### Bridge Communication
```python
from integration.core_bridge import CoreBridge
bridge = CoreBridge()
response = bridge.forward_creator_request("user123", {"prompt": "Hello"})
print(response)
```

## 🔒 Safety Features

### Rollback Safety
- Delete `integration/` folder to remove integration
- Both projects continue working independently
- No impact on original functionality

### Error Handling
- All HTTP calls have timeout protection
- Graceful failure when services unavailable
- No data corruption on failures

### Independence
- Core Integrator runs standalone
- Creator Core runs standalone  
- Integration layer is optional

## 📋 Troubleshooting

### Services Not Starting
1. Check port availability (8000, 5002)
2. Verify Python dependencies installed
3. Check for conflicting processes

### Integration Errors
1. Ensure both services are running
2. Verify network connectivity
3. Check service URLs in config

### Health Check Failures
1. Confirm service endpoints accessible
2. Check firewall settings
3. Verify service startup completion

## 🎯 Demo Readiness

**Both services must be running for integration to work:**
1. Start Core Integrator: `python main.py`
2. Start Creator Core: `python app.py`  
3. Use integration layer as needed
4. Services remain independent and demo-ready