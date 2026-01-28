# SERVICE_OUTPUTS.md

## Service Outputs Documentation

This document specifies all outputs produced by the Core Integrator microservice.

### HTTP Response Formats

All endpoints return JSON responses with consistent structure and error handling.

#### Core Processing Response

**Endpoint**: `POST /core`

**Success Response** (HTTP 200):
```json
{
  "status": "success",
  "message": "<string>",
  "result": {
    // Agent-specific result data
  }
}
```

**Error Response** (HTTP 500):
```json
{
  "status": "error",
  "message": "<error description>",
  "result": {}
}
```

**Field Specifications**:

| Field | Type | Always Present | Description |
|-------|------|----------------|-------------|
| `status` | string | Yes | Either "success" or "error" |
| `message` | string | Yes | Human-readable status message |
| `result` | object | Yes | Agent-specific result data (empty object on error) |

#### History Retrieval Response

**Endpoint**: `GET /get-history`

**Success Response** (HTTP 200):
```json
[
  {
    "module": "<string>",
    "timestamp": "<ISO datetime string>",
    "response": {
      "status": "success",
      "message": "<string>",
      "result": {
        // Sanitized response data
      }
    }
  }
]
```

**Error Response** (HTTP 500):
```json
{
  "detail": "History retrieval failed"
}
```

**Response Characteristics**:
- Returns array of last 10 interactions
- Each interaction has `module`, `timestamp`, `response`
- Response data is security-sanitized
- Chronological order (newest first)

#### Context Retrieval Response

**Endpoint**: `GET /get-context`

**Success Response** (HTTP 200):
```json
[
  {
    "module": "<string>",
    "timestamp": "<ISO datetime string>",
    "response": {
      "status": "success",
      "message": "<string>",
      "result": {
        // Sanitized response data
      }
    }
  }
]
```

**Error Response** (HTTP 500):
```json
{
  "detail": "Context retrieval failed"
}
```

**Response Characteristics**:
- Returns array of last 3 interactions
- Same structure as history endpoint
- Used for providing context to agents

#### Creator History Response

**Endpoint**: `GET /creator/history`

**Success Response** (HTTP 200):
```json
{
  // Noopur history response or local fallback
}
```

**Error Response** (HTTP 500):
```json
{
  "detail": "History retrieval failed"
}
```

**Response Characteristics**:
- Forwards Noopur history response when available
- Falls back to local history when Noopur unavailable
- Response format depends on Noopur service

#### Feedback Submission Response

**Endpoint**: `POST /feedback`

**Success Response** (HTTP 200):
```json
{
  "status": "received",
  "message": "Feedback processed successfully",
  "result": {
    // Noopur response data or local confirmation
  }
}
```

**Error Response** (HTTP 500):
```json
{
  "detail": "Feedback processing failed"
}
```

**Response Characteristics**:
- Forwards Noopur feedback response when available
- Returns local confirmation when Noopur disabled
- Feedback is always stored locally regardless

#### Root Endpoint Response

**Endpoint**: `GET /`

**Response** (HTTP 200):
```json
{
  "message": "Unified Backend Bridge API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### Health Check Responses

#### Health Endpoint

**Endpoint**: `GET /system/health`

**Purpose**: Binary operational status for load balancers and monitoring

**Healthy Response** (HTTP 200):
```json
{
  "status": "ok",
  "dependencies": {
    "database": "up" | "down",
    "gateway": "up" | "down",
    "noopur": "up" | "down" | "disabled",
    "video_service": "up" | "down" | "disabled"
  },
  "timestamp": "<ISO datetime string>Z"
}
```

**Unhealthy Response** (HTTP 200):
```json
{
  "status": "down",
  "dependencies": {
    "database": "up" | "down",
    "gateway": "up" | "down",
    "noopur": "up" | "down" | "disabled",
    "video_service": "up" | "down" | "disabled"
  },
  "timestamp": "<ISO datetime string>Z"
}
```

**Health Logic**:
- `status: "ok"` when all dependencies are "up" or "disabled"
- `status: "down"` when any critical dependency is "down"
- All dependencies are checked on every health request
- Response is always HTTP 200 (status indicates health, not HTTP status)

**Dependency Status Values**:
- `"up"`: Service is responding correctly
- `"down"`: Service is unreachable or returning errors
- `"disabled"`: Service integration is disabled via configuration

### Diagnostics Responses

#### Diagnostics Endpoint

**Endpoint**: `GET /system/diagnostics`

**Purpose**: Detailed system information for debugging and monitoring

**Response** (HTTP 200):
```json
{
  "config": {
    "db_mode": "sqlite" | "mongodb" | "noopur",
    "noopur_enabled": true | false,
    "video_service_url": "<string>",
    "log_level": "<string>",
    "sspl_enabled": true | false
  },
  "database": {
    "status": "connected" | "<error message>",
    "latency_ms": <number> | null,
    "adapter": "<adapter class name>"
  },
  "agents": {
    "finance": "loaded" | null,
    "education": "loaded" | null,
    "creator": "loaded" | null,
    "video": "loaded" | null
  },
  "feature_flags": {
    "sspl_enabled": true | false,
    "noopur_integration": true | false,
    "mongodb_enabled": true | false
  },
  "timestamp": "<ISO datetime string>Z"
}
```

### Log Retrieval Responses

#### Latest Logs Endpoint

**Endpoint**: `GET /system/logs/latest`

**Success Response** (HTTP 200):
```json
{
  "log_file": "<absolute path to log file>",
  "entries": [
    "<log line 1>",
    "<log line 2>",
    // ... up to limit
  ],
  "count": <number of entries returned>
}
```

**No Logs Response** (HTTP 200):
```json
{
  "logs": [],
  "message": "No logs available"
}
```

**Error Response** (HTTP 500):
```json
{
  "error": "<error message>"
}
```

### Agent-Specific Response Formats

#### Creator Agent Responses

**Generate Intent**:
```json
{
  "status": "success",
  "message": "Content generated successfully",
  "result": {
    "generated_text": "<string>",
    "generation_id": <integer>,
    "metadata": {
      "word_count": <integer>,
      "topic": "<string>",
      "type": "<string>"
    }
  }
}
```

**History Intent**:
```json
{
  "status": "success",
  "message": "History retrieved",
  "result": {
    // Noopur history format or local fallback
  }
}
```

#### Finance Agent Responses

**Generate Intent**:
```json
{
  "status": "success",
  "message": "Financial analysis complete",
  "result": {
    "analysis": "<string>",
    "recommendations": ["<string>"],
    "risk_level": "low" | "medium" | "high"
  }
}
```

#### Education Agent Responses

**Generate Intent**:
```json
{
  "status": "success",
  "message": "Educational content created",
  "result": {
    "content": "<string>",
    "learning_objectives": ["<string>"],
    "difficulty_level": "beginner" | "intermediate" | "advanced"
  }
}
```

#### Video Agent Responses

**Generate Intent**:
```json
{
  "status": "success",
  "message": "Video generation initiated",
  "result": {
    "video_url": "<string>",
    "duration_seconds": <number>,
    "fallback_used": true | false
  }
}
```

**List Videos Intent**:
```json
{
  "status": "success",
  "message": "Videos retrieved",
  "result": {
    "videos": [
      {
        "id": "<string>",
        "title": "<string>",
        "url": "<string>",
        "created_at": "<ISO datetime>"
      }
    ]
  }
}
```

### Degraded Mode Outputs

When external services are unavailable, the service provides fallback responses:

#### Noopur Unavailable (Creator Module)
```json
{
  "status": "success",
  "message": "Content generated (limited context)",
  "result": {
    "generated_text": "<string>",
    "generation_id": null,
    "metadata": {
      "context_available": false,
      "fallback_mode": true
    }
  }
}
```

#### Video Service Unavailable
```json
{
  "status": "success",
  "message": "Video generation failed, providing text alternative",
  "result": {
    "generated_text": "<string>",
    "video_url": null,
    "fallback_used": true,
    "error": "Video service unavailable"
  }
}
```

### Error Response Formats

#### Validation Errors (HTTP 422)
```json
{
  "detail": [
    {
      "loc": ["body", "module"],
      "msg": "value is not a valid enumeration member",
      "type": "type_error.enum",
      "ctx": {
        "enum_values": ["finance", "education", "creator", "sample_text", "video"]
      }
    }
  ]
}
```

#### Security Validation Errors (HTTP 400)
```json
{
  "detail": "Invalid user identifier"
}
```

#### SSPL Validation Errors (HTTP 401)
```json
{
  "detail": "SSPL validation failed"
}
```

#### Processing Errors (HTTP 500)
```json
{
  "detail": "Processing failed"
}
```

### Log and Telemetry Events

The service emits structured JSON logs to files in `logs/bridge/` directory.

#### Request Processing Logs
```json
{
  "level": "INFO",
  "logger": "src.core.gateway",
  "message": "Processing request for module: creator, intent: generate",
  "extra": {
    "user_id": "user123",
    "request_data": {
      "module": "creator",
      "intent": "generate",
      "data": {
        "topic": "AI",
        "goal": "educational"
      }
    }
  }
}
```

#### External Service Call Logs
```json
{
  "level": "INFO",
  "logger": "src.utils.noopur_client",
  "message": "Noopur generate successful",
  "extra": {
    "dependency": "noopur",
    "endpoint": "/generate",
    "latency_ms": 150.5
  }
}
```

#### Error Logs
```json
{
  "level": "ERROR",
  "logger": "src.utils.noopur_client",
  "message": "Noopur generate timeout",
  "extra": {
    "dependency": "noopur",
    "endpoint": "/generate",
    "error_type": "timeout",
    "timeout_seconds": 30
  }
}
```

#### Response Logs
```json
{
  "level": "INFO",
  "logger": "src.core.gateway",
  "message": "Request processed with status: success",
  "extra": {
    "user_id": "user123",
    "response_data": {
      "status": "success",
      "message": "Content generated successfully",
      "result": {
        "generated_text": "...",
        "generation_id": 12345
      }
    }
  }
}
```

### Data Storage Outputs

The service stores interaction data that can be retrieved via history endpoints:

#### Stored Interaction Format
```json
{
  "user_id": "<string>",
  "module": "<string>",
  "intent": "<string>",
  "timestamp": "<ISO datetime>",
  "request_data": {
    // Original request data
  },
  "response_data": {
    // Normalized response data
  }
}
```

### Reliability Guarantees

#### Response Consistency
- All endpoints return valid JSON
- Error responses maintain the same structure as success responses
- No endpoint returns HTML or plain text

#### Data Persistence
- All interactions are stored locally (SQLite/MongoDB)
- History retrieval is guaranteed for stored interactions
- No data loss during external service failures

#### External Service Guarantees
- Noopur failures don't prevent basic functionality
- Video service failures provide text fallbacks
- Health checks are non-blocking and fast

#### Performance Guarantees
- Health checks complete in < 1 second
- Normal requests complete in < 5 seconds
- Degraded mode responses are immediate

This documentation ensures downstream services and clients can reliably depend on the service's output formats and behavior.</content>
<parameter name="filePath">c:\Aman\Core-Integrator-Sprint-1.1-\SERVICE_OUTPUTS.md