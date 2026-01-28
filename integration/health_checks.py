"""
Health Checks
Aggregates health status from both services
"""
import requests
from typing import Dict, Any

class HealthChecker:
    def __init__(self, 
                 core_integrator_url: str = "http://localhost:8000",
                 creator_core_url: str = "http://localhost:5002"):
        self.core_url = core_integrator_url.rstrip('/')
        self.creator_url = creator_core_url.rstrip('/')
    
    def check_core_integrator(self) -> Dict[str, Any]:
        """Check Core Integrator health"""
        try:
            response = requests.get(f"{self.core_url}/system/health", timeout=10)
            if response.status_code == 200:
                return {"status": "up", "details": response.json()}
            else:
                return {"status": "down", "error": f"HTTP {response.status_code}"}
        except requests.RequestException as e:
            return {"status": "down", "error": str(e)}
    
    def check_creator_core(self) -> Dict[str, Any]:
        """Check Creator Core health via history endpoint"""
        try:
            response = requests.get(f"{self.creator_url}/history", timeout=10)
            if response.status_code == 200:
                return {"status": "up", "details": "History endpoint accessible"}
            else:
                return {"status": "down", "error": f"HTTP {response.status_code}"}
        except requests.RequestException as e:
            return {"status": "down", "error": str(e)}
    
    def aggregate_health(self) -> Dict[str, Any]:
        """Get combined health status"""
        core_health = self.check_core_integrator()
        creator_health = self.check_creator_core()
        
        overall_status = "up" if (
            core_health["status"] == "up" and 
            creator_health["status"] == "up"
        ) else "down"
        
        return {
            "overall_status": overall_status,
            "services": {
                "core_integrator": core_health,
                "creator_core": creator_health
            }
        }