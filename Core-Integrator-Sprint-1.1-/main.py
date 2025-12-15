from fastapi import FastAPI, HTTPException, Depends
from typing import List, Dict, Any, Optional
import os
import sqlite3
from pathlib import Path
from src.core.models import CoreRequest, CoreResponse
from src.core.gateway import Gateway
from src.db.memory import ContextMemory
from config.config import DB_PATH

# Optional SSPL - can be disabled for testing
SSPL_ENABLED = os.getenv("SSPL_ENABLED", "false").lower() in ("true", "1", "yes")

if SSPL_ENABLED:
    from src.utils.sspl_dependency import require_sspl
else:
    async def require_sspl():
        return True

app = FastAPI(
    title="Unified Backend Bridge",
    description="Central orchestration layer for Finance, Education, and Creator agents",
    version="1.0.0"
)

# Initialize gateway and memory
gateway = Gateway()
memory = ContextMemory(DB_PATH)

@app.post("/core", response_model=CoreResponse)
async def core_endpoint(request: CoreRequest, _sspl=Depends(require_sspl)) -> CoreResponse:
    """Main gateway endpoint for processing agent requests"""
    try:
        response = gateway.process_request(
            module=request.module,
            intent=request.intent, 
            user_id=request.user_id,
            data=request.data
        )
        # Validate response structure before creating CoreResponse
        if not isinstance(response, dict) or 'status' not in response:
            raise HTTPException(status_code=500, detail="Invalid agent response format")
        
        # Ensure required fields exist
        response.setdefault('message', 'No message provided')
        response.setdefault('result', {})
        
        return CoreResponse(**response)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Response validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-history")
async def get_history(user_id: str) -> List[Dict[str, Any]]:
    """Get full interaction history for a user"""
    try:
        history = memory.get_user_history(user_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-context") 
async def get_context(user_id: str) -> List[Dict[str, Any]]:
    """Get recent context (last 3 interactions) for a user"""
    try:
        context = memory.get_context(user_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Unified Backend Bridge API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/system/health")
async def system_health():
    """System health check"""
    try:
        # Check database connectivity
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("SELECT 1").fetchone()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "components": {
            "database": db_status,
            "gateway": "healthy",
            "modules": len(gateway.agents)
        }
    }

@app.get("/system/diagnostics")
async def system_diagnostics():
    """System diagnostics and module information"""
    # Get loaded modules
    modules_info = {name: type(agent).__name__ for name, agent in gateway.agents.items()}
    
    # Get memory stats
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM interactions")
            total_interactions = cursor.fetchone()[0]
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) FROM interactions")
            unique_users = cursor.fetchone()[0]
    except Exception:
        total_interactions = 0
        unique_users = 0
    
    # Check security components
    nonce_db_exists = os.path.exists("data/nonce_store.db")
    
    return {
        "modules": modules_info,
        "memory": {
            "total_interactions": total_interactions,
            "unique_users": unique_users,
            "db_path": DB_PATH
        },
        "security": {
            "nonce_store_enabled": nonce_db_exists,
            "sspl_middleware": True
        },
        "version": "1.0.0"
    }

@app.get("/system/logs/latest")
async def system_logs_latest(limit: int = 50):
    """Get latest log entries"""
    log_dir = Path("logs/bridge")
    if not log_dir.exists():
        return {"logs": [], "message": "No logs available"}
    
    log_files = sorted(log_dir.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
    if not log_files:
        return {"logs": [], "message": "No log files found"}
    
    latest_log = log_files[0]
    try:
        with open(latest_log, 'r') as f:
            lines = f.readlines()[-limit:]
        return {
            "log_file": str(latest_log),
            "entries": [line.strip() for line in lines],
            "count": len(lines)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)