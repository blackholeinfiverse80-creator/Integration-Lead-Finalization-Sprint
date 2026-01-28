"""
Core Bridge
Connects Core Integrator to Creator Core via HTTP
"""
import requests
from typing import Dict, Any, Optional
from creator_client import CreatorClient

class CoreBridge:
    def __init__(self, 
                 core_integrator_url: str = "http://localhost:8000",
                 creator_core_url: str = "http://localhost:5002"):
        self.core_url = core_integrator_url.rstrip('/')
        self.creator_client = CreatorClient(creator_core_url)
    
    def forward_creator_request(self, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Forward creator request from Core Integrator to Creator Core"""
        prompt = data.get('prompt', '')
        if not prompt:
            return None
        
        # Call Creator Core
        creator_response = self.creator_client.generate(prompt)
        if not creator_response:
            return None
        
        # Forward to Core Integrator
        try:
            response = requests.post(
                f"{self.core_url}/core",
                json={
                    "module": "creator",
                    "intent": "generate",
                    "user_id": user_id,
                    "data": creator_response
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def forward_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Forward feedback from Core Integrator to Creator Core"""
        generation_id = feedback_data.get('generation_id')
        command = feedback_data.get('command')
        
        if not generation_id or not command:
            return None
        
        # Submit to Creator Core
        creator_response = self.creator_client.submit_feedback(generation_id, command)
        if not creator_response:
            return None
        
        # Forward to Core Integrator
        try:
            response = requests.post(
                f"{self.core_url}/feedback",
                json={
                    "user_id": user_id,
                    "generation_id": generation_id,
                    "rating": 5 if command.startswith('+') else 1,
                    "comment": f"Feedback: {command}"
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None