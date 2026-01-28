"""
Creator Core HTTP Client
Thin adapter for calling Creator Core API endpoints
"""
import requests
import json
from typing import Dict, Any, Optional

class CreatorClient:
    def __init__(self, base_url: str = "http://localhost:5002"):
        self.base_url = base_url.rstrip('/')
    
    def generate(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Creator Core /generate endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/generate",
                json={"prompt": prompt},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def submit_feedback(self, generation_id: int, command: str) -> Optional[Dict[str, Any]]:
        """Call Creator Core /feedback endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/feedback",
                json={"generation_id": generation_id, "command": command},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def get_history(self) -> Optional[list]:
        """Call Creator Core /history endpoint"""
        try:
            response = requests.get(f"{self.base_url}/history", timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None