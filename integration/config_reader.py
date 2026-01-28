"""
Config Reader
Reads existing configuration from both projects
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigReader:
    def __init__(self):
        self.core_integrator_path = Path("../Core-Integrator-Sprint-1.1-")
        self.creator_core_path = Path("../creator-core")
    
    def read_core_integrator_config(self) -> Dict[str, Any]:
        """Read Core Integrator .env file"""
        env_file = self.core_integrator_path / ".env"
        config = {}
        
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            except Exception:
                pass
        
        # Add defaults
        config.setdefault('CORE_INTEGRATOR_PORT', '8000')
        config.setdefault('SSPL_ENABLED', 'true')
        config.setdefault('DB_PATH', 'db/context.db')
        
        return config
    
    def read_creator_core_config(self) -> Dict[str, Any]:
        """Read Creator Core configuration"""
        config = {
            'CREATOR_CORE_PORT': '5002',
            'FLASK_ENV': 'development',
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///context_intelligence.db'
        }
        return config
    
    def get_service_urls(self) -> Dict[str, str]:
        """Get service URLs from configs"""
        core_config = self.read_core_integrator_config()
        creator_config = self.read_creator_core_config()
        
        return {
            'core_integrator': f"http://localhost:{core_config.get('CORE_INTEGRATOR_PORT', '8000')}",
            'creator_core': f"http://localhost:{creator_config.get('CREATOR_CORE_PORT', '5002')}"
        }
    
    def validate_configs(self) -> Dict[str, bool]:
        """Validate that both project configs are accessible"""
        return {
            'core_integrator_exists': self.core_integrator_path.exists(),
            'creator_core_exists': self.creator_core_path.exists(),
            'core_env_exists': (self.core_integrator_path / ".env").exists()
        }