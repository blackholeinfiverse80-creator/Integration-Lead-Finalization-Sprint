"""
Bridge Client for CreatorCore Communication
Handles HTTP communication with retry logic and error handling
"""

import requests
import time
from typing import Dict, Any, Optional
from enum import Enum

class ErrorType(Enum):
    NETWORK = "network"
    LOGIC = "logic" 
    SCHEMA = "schema"
    UNEXPECTED = "unexpected"

class BridgeClient:
    """HTTP client for CreatorCore backend communication"""
    
    def __init__(self, base_url: str = "http://localhost:5002", timeout: int = 5):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     retries: int = 3) -> Dict[str, Any]:
        """Make HTTP request with retry logic and error handling"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, timeout=self.timeout)
                elif method.upper() == 'POST':
                    response = self.session.post(url, json=data, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.ConnectionError as e:
                error_type = ErrorType.NETWORK
                if attempt == retries - 1:
                    return self._handle_error(error_type, str(e), endpoint)
                time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                
            except requests.exceptions.Timeout as e:
                error_type = ErrorType.NETWORK
                if attempt == retries - 1:
                    return self._handle_error(error_type, f"Timeout after {self.timeout}s", endpoint)
                time.sleep(0.5 * (attempt + 1))
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    error_type = ErrorType.SCHEMA
                elif e.response.status_code in [404, 405]:
                    error_type = ErrorType.LOGIC
                else:
                    error_type = ErrorType.UNEXPECTED
                return self._handle_error(error_type, str(e), endpoint)
                
            except Exception as e:
                error_type = ErrorType.UNEXPECTED
                if attempt == retries - 1:
                    return self._handle_error(error_type, str(e), endpoint)
                time.sleep(0.5 * (attempt + 1))
        
        return self._handle_error(ErrorType.NETWORK, "Max retries exceeded", endpoint)
    
    def _handle_error(self, error_type: ErrorType, message: str, endpoint: str) -> Dict[str, Any]:
        """Handle and classify errors with fallback response"""
        return {
            "success": False,
            "error_type": error_type.value,
            "error_message": message,
            "endpoint": endpoint,
            "fallback_used": True
        }
    
    def log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send log data to CreatorCore"""
        return self._make_request('POST', '/core/log', data)
    
    def feedback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send feedback data to CreatorCore"""
        return self._make_request('POST', '/core/feedback', data)
    
    def get_context(self, limit: int = 3) -> Dict[str, Any]:
        """Get context data from CreatorCore"""
        endpoint = f'/core/context?limit={limit}'
        return self._make_request('GET', endpoint)
    
    def health_check(self) -> Dict[str, Any]:
        """Check CreatorCore health status"""
        return self._make_request('GET', '/system/health')
    
    def is_healthy(self) -> bool:
        """Quick health check returning boolean"""
        try:
            result = self.health_check()
            return result.get('status') == 'healthy'
        except:
            return False