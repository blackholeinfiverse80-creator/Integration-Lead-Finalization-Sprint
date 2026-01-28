# Core Integrator

A smart routing service that connects different AI agents for finance, education, and content creation.

## What It Does

This service acts as a central hub that:
- Routes requests to specialized AI agents
- Manages user conversation history
- Connects to external services safely
- Provides health monitoring

## Quick Start

1. **Install**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env
   ```

2. **Run**:
   ```bash
   python main.py
   ```

3. **Test**: Visit http://localhost:8001/system/health

## Main Features

- **Smart Routing**: Automatically sends requests to the right AI agent
- **Memory**: Remembers conversation context for better responses
- **Security**: Built-in security validation and safe data handling
- **Monitoring**: Health checks and system diagnostics
- **Flexible Storage**: Works with local files or cloud databases

## API Usage

Send requests to `/core` with:
```json
{
  "module": "finance",
  "intent": "analyze",
  "data": {"query": "What's my spending pattern?"}
}
```

## Configuration

Basic settings in `.env` file:
- `USE_MONGODB=true` - Use cloud database
- `INTEGRATOR_USE_NOOPUR=true` - Enable enhanced features
- `SSPL_ENABLED=true` - Enable security validation

## Status

✅ Production ready  
✅ All tests passing  
✅ Security validated  
✅ Performance optimized

For technical details, see `PROJECT_OVERVIEW.md` and `DEPLOYMENT.md`.