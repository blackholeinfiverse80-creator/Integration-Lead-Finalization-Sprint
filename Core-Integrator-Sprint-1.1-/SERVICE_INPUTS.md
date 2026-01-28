# SERVICE_INPUTS.md

## Service Inputs Documentation

This document specifies all inputs required to run and use the Core Integrator microservice.

### Startup Inputs (Environment Variables)

The service validates critical configuration on startup and fails fast if required variables are missing.

#### Required Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| (none) | - | - | No variables are strictly required for basic operation |

#### Optional Environment Variables

| Variable | Type | Default | Required When | Description |
|----------|------|---------|---------------|-------------|
| `DB_PATH` | string | `"data/context.db"` | - | SQLite database file path |
| `USE_MONGODB` | boolean | `"false"` | When using MongoDB | Enable MongoDB adapter instead of SQLite |
| `MONGODB_CONNECTION_STRING` | string | `"mongodb://localhost:27017"` | When `USE_MONGODB=true` | MongoDB connection URI |
| `MONGODB_DATABASE_NAME` | string | `"core_integrator"` | When `USE_MONGODB=true` | MongoDB database name |
| `INTEGRATOR_USE_NOOPUR` | boolean | `"false"` | When enabling Noopur integration | Enable Noopur context enhancement |
| `NOOPUR_BASE_URL` | string | `"http://localhost:5001"` | When `INTEGRATOR_USE_NOOPUR=true` | Noopur service base URL |
| `NOOPUR_API_KEY` | string | `""` | When `INTEGRATOR_USE_NOOPUR=true` | Authentication token for Noopur |
| `VIDEO_SERVICE_URL` | string | `"http://localhost:5002"` | - | Text-to-video service base URL |
| `VIDEO_SERVICE_TIMEOUT` | integer | `"300"` | - | Timeout for video service calls (seconds) |
| `LOG_LEVEL` | string | `"INFO"` | - | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `SSPL_ENABLED` | boolean | `"false"` | When using signed payloads | Enable Signed Secure Payload validation |
| `SSPL_ALLOW_DRIFT_SECONDS` | integer | `"300"` | When `SSPL_ENABLED=true` | Allowed timestamp drift for SSPL validation |

#### Boolean Value Format
- Truthy values: `"1"`, `"true"`, `"yes"` (case-insensitive)
- Falsy values: `"0"`, `"false"`, `"no"`, `""` (case-insensitive)

#### Startup Validation Rules

**Critical Variables Check**:
- If `USE_MONGODB=true`: `MONGODB_CONNECTION_STRING` must be set
- If `INTEGRATOR_USE_NOOPUR=true`: `NOOPUR_BASE_URL` and `NOOPUR_API_KEY` must be set
- `VIDEO_SERVICE_URL` must always be set (has default)

**Failure Behavior**:
- Service exits with error code 1
- Error message: `"Missing critical environment variables: {list}"`
- No partial startup or degraded modes

### Runtime Inputs (HTTP Requests)

The service exposes several HTTP endpoints, each with specific input requirements.

#### Core Processing Endpoint

**Endpoint**: `POST /core`

**Purpose**: Main gateway for processing agent requests

**Content-Type**: `application/json`

**Required Headers**:
```
User-Id: <string>  # Must be present in request headers, not JSON body
```

**Request Body Schema**:

```json
{
  "module": "finance" | "education" | "creator" | "sample_text" | "video",
  "intent": "generate" | "analyze" | "review" | "get_status" | "list_videos" | "feedback" | "history",
  "user_id": "<string, min_length=1>",
  "data": {
    // Module-specific data object
  }
}
```

**Field Validation Rules**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `module` | string | Yes | Must be one of: finance, education, creator, sample_text, video | Target agent module |
| `intent` | string | Yes | Must be one of: generate, analyze, review, get_status, list_videos, feedback, history | Action to perform |
| `user_id` | string | Yes | Minimum length 1 | User identifier (also required in header) |
| `data` | object | No | Any valid JSON object | Module-specific parameters |

**Module-Specific Data Requirements**:

**Creator Module** (`module: "creator"`):
```json
{
  "topic": "<string>",      // Optional: Content topic
  "goal": "<string>",       // Optional: Content goal/purpose
  "type": "<string>"        // Optional: Content type (default: "story")
}
```

**Feedback Intent** (`intent: "feedback"`):
```json
{
  "generation_id": "<integer>",  // Required: ID of generation to feedback on
  "command": "+2" | "+1" | "-1" | "-2",  // Required: Feedback rating
  "user_id": "<string>",         // Required: User providing feedback
  "comment": "<string>"          // Optional: Feedback comment (max 500 chars)
}
```

#### History Retrieval Endpoint

**Endpoint**: `GET /get-history?user_id=<string>`

**Purpose**: Get user's interaction history

**Required Query Parameters**:
- `user_id`: User identifier (string, minimum length 1)

**Headers**: None required

#### Context Retrieval Endpoint

**Endpoint**: `GET /get-context?user_id=<string>`

**Purpose**: Get user's recent context (last 3 interactions)

**Required Query Parameters**:
- `user_id`: User identifier (string, minimum length 1)

**Headers**: None required

#### Creator History Endpoint

**Endpoint**: `GET /creator/history?user_id=<string>`

**Purpose**: Get creator-specific generation history

**Required Query Parameters**:
- `user_id`: User identifier (string, minimum length 1)

**Headers**: None required

#### Feedback Submission Endpoint

**Endpoint**: `POST /feedback`

**Purpose**: Submit feedback for generated content

**Content-Type**: `application/json`

**Request Body Schema**:

```json
{
  "generation_id": "<integer, must be > 0>",
  "command": "+2" | "+1" | "-1" | "-2",
  "user_id": "<string, min_length=1>",
  "comment": "<string, optional, max_length=500>",
  "timestamp": "<ISO datetime string, optional>"
}
```

**Field Validation Rules**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| `generation_id` | integer | Yes | Must be > 0 | ID of the generation to provide feedback for |
| `command` | string | Yes | Must be one of: +2, +1, -1, -2 | Feedback rating (+2=excellent, -2=terrible) |
| `user_id` | string | Yes | Minimum length 1 | User providing feedback |
| `comment` | string | No | Maximum length 500 | Optional feedback comment |
| `timestamp` | string | No | ISO datetime format | Auto-generated if not provided |

#### System Endpoints

**Health Check**: `GET /system/health`
- No inputs required
- Returns operational status

**Diagnostics**: `GET /system/diagnostics`
- No inputs required
- Returns detailed system information

**Latest Logs**: `GET /system/logs/latest?limit=<integer>`
- Optional query parameter: `limit` (default: 50, max: 1000)
- Returns recent log entries

### External Service Dependencies

The service depends on external services that must be reachable for full functionality.

#### Noopur Service (Optional)
- **Purpose**: Enhanced context and content generation
- **Endpoint**: Configured via `NOOPUR_BASE_URL`
- **Authentication**: Bearer token via `NOOPUR_API_KEY`
- **Required When**: `INTEGRATOR_USE_NOOPUR=true`
- **Degradation**: Service works without Noopur (returns empty context)

#### Video Service (Optional)
- **Purpose**: Text-to-video conversion
- **Endpoint**: Configured via `VIDEO_SERVICE_URL`
- **Authentication**: None
- **Required When**: Making video generation requests
- **Degradation**: Video requests fall back to text-only responses

#### MongoDB (Optional)
- **Purpose**: Distributed context storage
- **Connection**: Configured via `MONGODB_CONNECTION_STRING`
- **Required When**: `USE_MONGODB=true`
- **Degradation**: Falls back to SQLite storage

### Input Validation and Error Handling

#### Malformed JSON
- **Behavior**: HTTP 422 Unprocessable Entity
- **Response**: `{"detail": "JSON decode error"}`

#### Missing Required Fields
- **Behavior**: HTTP 422 Unprocessable Entity
- **Response**: Pydantic validation error details

#### Invalid Field Values
- **Behavior**: HTTP 422 Unprocessable Entity
- **Response**: Pydantic validation error with specific field violations

#### Security Validation Failures
- **Behavior**: HTTP 400 Bad Request
- **Response**: `{"detail": "Invalid user identifier"}`

#### SSPL Validation Failures (when enabled)
- **Behavior**: HTTP 401 Unauthorized
- **Response**: `{"detail": "SSPL validation failed"}`

#### Missing User-Id Header
- **Behavior**: HTTP 500 Internal Server Error
- **Response**: `{"detail": "Processing failed"}` (logged as security validation failure)

### Example Requests

#### Basic Creator Request
```bash
curl -X POST http://localhost:8001/core \
  -H "Content-Type: application/json" \
  -H "User-Id: user123" \
  -d '{
    "module": "creator",
    "intent": "generate",
    "user_id": "user123",
    "data": {
      "topic": "artificial intelligence",
      "goal": "educational content",
      "type": "article"
    }
  }'
```

#### Feedback Submission
```bash
curl -X POST http://localhost:8001/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "generation_id": 12345,
    "command": "+1",
    "user_id": "user123",
    "comment": "Good content but could be more detailed"
  }'
```

#### History Retrieval
```bash
curl "http://localhost:8001/get-history?user_id=user123"
```

### Environment Setup Examples

#### Minimal Configuration (SQLite + No External Services)
```bash
export VIDEO_SERVICE_URL="http://localhost:5002"
python main.py
```

#### Full Configuration (MongoDB + Noopur + Security)
```bash
export USE_MONGODB="true"
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017"
export MONGODB_DATABASE_NAME="core_integrator"
export INTEGRATOR_USE_NOOPUR="true"
export NOOPUR_BASE_URL="http://noopur-service:5001"
export NOOPUR_API_KEY="your-api-key"
export VIDEO_SERVICE_URL="http://video-service:5002"
export SSPL_ENABLED="true"
export LOG_LEVEL="DEBUG"
python main.py
```

This configuration ensures the service can be deployed and operated correctly on the first attempt.</content>
<parameter name="filePath">c:\Aman\Core-Integrator-Sprint-1.1-\SERVICE_INPUTS.md