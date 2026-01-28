# PROJECT_OVERVIEW.md

## Core Integrator Microservice

### Service Identity and Purpose

The Core Integrator is an independently deployable FastAPI microservice that serves as the central orchestration layer for a distributed AI agent system. It acts as a unified gateway that routes requests to specialized AI agents (Finance, Education, Creator, Video) while managing user context, external service integrations, and providing a consistent API surface.

**Primary Responsibility**: Request routing, context management, and external service orchestration for AI agent interactions.

**Non-Responsibilities**:
- Direct AI model inference or content generation
- User authentication or session management
- Data persistence beyond interaction history
- Real-time communication or WebSocket handling

### System Architecture Position

The Core Integrator sits at the center of a distributed system with the following architectural relationships:

```
[Client Applications]
        │
        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Core Integrator │───▶│   AI Agents     │───▶│ External Services│
│   (FastAPI)      │    │ (Finance, Edu,  │    │ (Noopur, Video) │
└─────────────────┘    │ Creator, Video) │    └─────────────────┘
        │              └─────────────────┘             │
        ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Context DB    │    │   Bridge Client │    │   Noopur API    │
│  (SQLite/Mongo) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Upstream Dependencies**:
- Client applications making HTTP requests
- Noopur backend service (optional, for enhanced context)
- Video generation service (optional, for text-to-video)

**Downstream Dependencies**:
- AI agent modules (FinanceAgent, EducationAgent, CreatorAgent, VideoAgent)
- Context storage (SQLite or MongoDB)
- External service clients (BridgeClient, VideoBridgeClient, NoopurClient)

### Request Flow Architecture

Every request follows this exact sequence through the system:

#### 1. HTTP Ingress (main.py)
- Request arrives at FastAPI endpoint (`/core`)
- Security middleware validates user_id from request headers
- Request is validated against `CoreRequest` Pydantic schema
- Optional SSPL (Signed Secure Payload) validation if enabled

#### 2. Gateway Processing (gateway.py)
- Gateway receives: `module`, `intent`, `user_id`, `data`
- User context is retrieved from memory adapter
- For creator module: CreatorRouter performs pre-warming with Noopur context
- Request is routed to appropriate agent based on `module` field

#### 3. Agent Processing
- Agent receives: `intent`, `data`, `context`
- Agent processes request using its specific logic
- Response is returned in agent-specific format

#### 4. Response Normalization
- Gateway normalizes agent response into standardized `CoreResponse` format
- Interaction is stored in context database
- Response is sanitized for security
- HTTP response is returned to client

### Internal Components

#### Core Components

**Gateway (src/core/gateway.py)**
- Central routing logic
- Agent initialization and management
- Memory adapter selection (MongoDB > Noopur > SQLite priority)
- Response normalization
- External service health checking

**Agents (src/agents/)**
- `FinanceAgent`: Financial analysis and advice
- `EducationAgent`: Educational content and explanations
- `CreatorAgent`: Content generation with feedback loop
- `VideoAgent`: Text-to-video conversion
- Each agent implements `handle_request(intent, data, context)` method

**Memory Adapters (src/db/)**
- `SQLiteAdapter`: Local SQLite storage for context
- `MongoDBAdapter`: Distributed MongoDB storage
- `RemoteNoopurAdapter`: Context retrieval from Noopur service
- All implement `get_context()`, `store_interaction()`, `get_user_history()`

#### External Service Clients

**NoopurClient (src/utils/noopur_client.py)**
- Async HTTP client for Noopur backend integration
- Graceful degradation when service unavailable
- Methods: `generate()`, `feedback()`, `history()`, `health_check()`

**BridgeClient (src/utils/bridge_client.py)**
- HTTP client for legacy bridge service
- Synchronous requests with timeout handling

**VideoBridgeClient (src/utils/video_bridge_client.py)**
- HTTP client for text-to-video service
- Fallback handling for service unavailability

#### Routing Components

**CreatorRouter (creator_routing.py)**
- Pre-warming logic for creator requests
- Fetches context from Noopur before agent processing
- Handles feedback forwarding to Noopur

### Configuration Philosophy

The service follows strict environment-driven configuration with no hardcoded values:

#### Configuration Sources
- Environment variables only (no config files)
- Fail-fast validation on startup
- Configuration summary available via `/system/diagnostics`

#### Key Configuration Flags

**Database Selection**:
- `USE_MONGODB=true`: Use MongoDB adapter
- Default: SQLite adapter

**External Service Integration**:
- `INTEGRATOR_USE_NOOPUR=true`: Enable Noopur context enhancement
- `NOOPUR_BASE_URL`: Noopur service endpoint
- `NOOPUR_API_KEY`: Authentication for Noopur

**Security**:
- `SSPL_ENABLED=true`: Enable Signed Secure Payload validation
- `SSPL_ALLOW_DRIFT_SECONDS`: Timestamp drift tolerance

**Service Endpoints**:
- `VIDEO_SERVICE_URL`: Text-to-video service endpoint
- `MONGODB_CONNECTION_STRING`: MongoDB connection details

### Failure Handling Philosophy

#### Graceful Degradation
- External services are optional and degrade gracefully
- Noopur integration returns empty context when unavailable
- Video service falls back to text-only responses
- Database failures don't crash the service

#### Error Classification
- **Network errors**: Timeout, connection refused → Degraded mode
- **Service errors**: HTTP 5xx responses → Degraded mode
- **Client errors**: HTTP 4xx responses → Error responses
- **Validation errors**: Malformed requests → 400 Bad Request

#### Failure Responses
- Always return valid JSON responses
- Never expose internal errors to clients
- Log detailed error information for debugging
- Maintain API contract even during failures

### Health vs Diagnostics

#### Health Endpoint (`/system/health`)
- **Purpose**: Binary operational status for load balancers
- **Response**: `{"status": "ok|down", "dependencies": {...}, "timestamp": "..."}`
- **Logic**: All critical dependencies must be "up" or "disabled"
- **Frequency**: Called every 30 seconds by infrastructure

#### Diagnostics Endpoint (`/system/diagnostics`)
- **Purpose**: Detailed system information for monitoring/debugging
- **Response**: Configuration, latencies, agent status, feature flags
- **Logic**: Comprehensive system state snapshot
- **Frequency**: Called during deployments and incident response

### Logging and Observability

#### Structured Logging
- JSON format with consistent field names
- Request/response correlation via `user_id`
- Latency tracking for external service calls
- Error classification with `error_type` field

#### Log Events
- **Request ingress**: `{"user_id": "...", "request_data": {...}}`
- **External calls**: `{"dependency": "noopur", "endpoint": "/generate", "latency_ms": 150}`
- **Errors**: `{"error_type": "timeout", "dependency": "noopur"}`
- **Agent processing**: `{"user_id": "...", "response_data": {...}}`

#### Log Storage
- File-based logging to `logs/bridge/` directory
- Latest logs accessible via `/system/logs/latest` endpoint
- No log aggregation or external shipping (infrastructure responsibility)

### Design Decisions and Rationale

#### Why FastAPI?
- Native async support for external service calls
- Automatic OpenAPI documentation generation
- Pydantic integration for request/response validation
- High performance for I/O-bound operations

#### Why Multiple Memory Adapters?
- **Priority fallback**: MongoDB → Noopur → SQLite
- **Deployment flexibility**: Support various infrastructure setups
- **Migration path**: Can migrate data between adapters
- **Testing**: Easy to test with different storage backends

#### Why CreatorRouter Separation?
- Creator module has complex pre-warming logic
- Noopur integration is creator-specific
- Clean separation of concerns
- Easier testing of routing logic

#### Why No Direct AI Model Calls?
- **Separation of concerns**: Gateway routes, agents decide, external services generate
- **Scalability**: AI models can be scaled independently
- **Technology flexibility**: Can swap AI backends without changing gateway
- **Resource isolation**: Heavy AI workloads don't impact routing performance

### Explicit Non-Goals and Constraints

#### What This Service Does NOT Do
- **Authentication**: Delegates to infrastructure (API Gateway, reverse proxy)
- **Authorization**: Assumes authenticated user_id from headers
- **Rate limiting**: Infrastructure responsibility
- **Caching**: No application-level caching (use CDN/infrastructure)
- **Metrics aggregation**: Logs only, no statsd/graphite integration
- **Real-time features**: HTTP-only, no WebSockets or Server-Sent Events

#### Hard Constraints
- **No persistent connections**: HTTP-only architecture
- **No background jobs**: All processing is synchronous per request
- **No file uploads**: JSON-only request payloads
- **No HTML rendering**: API-only service
- **No database migrations**: Schema managed externally
- **No feature flags**: Configuration-driven enablement only

#### Performance Constraints
- **Response time**: < 5 seconds for normal operations
- **External timeouts**: 30 seconds maximum for Noopur calls
- **Memory usage**: < 500MB resident memory
- **Concurrent requests**: Designed for 100+ concurrent users

This service is designed for reliability, observability, and maintainability in a distributed system where the gateway must never be a single point of failure.</content>
<parameter name="filePath">c:\Aman\Core-Integrator-Sprint-1.1-\PROJECT_OVERVIEW.md