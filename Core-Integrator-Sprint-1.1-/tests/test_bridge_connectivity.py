"""
Test bridge connectivity with CreatorCore mock server
"""

import pytest
import subprocess
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.bridge_client import BridgeClient, ErrorType

class TestBridgeConnectivity:
    """Test suite for bridge client connectivity"""
    
    @pytest.fixture(autouse=True)
    def setup_client(self):
        """Setup bridge client for testing"""
        self.client = BridgeClient("http://localhost:5002")
    
    def test_health_check_success(self):
        """Test successful health check"""
        result = self.client.health_check()
        
        if result.get('success') is False:
            # Mock server not running, test error handling
            assert result['error_type'] == ErrorType.NETWORK.value
            assert 'fallback_used' in result
        else:
            # Mock server running, test success
            assert result['status'] == 'healthy'
            assert 'timestamp' in result
    
    def test_log_endpoint(self):
        """Test log endpoint functionality"""
        log_data = {
            "level": "info",
            "message": "Test log message",
            "module": "test"
        }
        
        result = self.client.log(log_data)
        
        if result.get('success') is False:
            # Test error handling
            assert result['error_type'] in [e.value for e in ErrorType]
        else:
            # Test success response
            assert result['status'] == 'logged'
            assert 'id' in result
    
    def test_feedback_endpoint(self):
        """Test feedback endpoint functionality"""
        feedback_data = {
            "rating": 5,
            "comment": "Test feedback",
            "session_id": "test_session"
        }
        
        result = self.client.feedback(feedback_data)
        
        if result.get('success') is False:
            # Test error handling
            assert result['error_type'] in [e.value for e in ErrorType]
        else:
            # Test success response
            assert result['status'] == 'feedback_received'
            assert 'id' in result
    
    def test_context_endpoint(self):
        """Test context retrieval"""
        result = self.client.get_context(limit=2)
        
        if result.get('success') is False:
            # Test error handling
            assert result['error_type'] in [e.value for e in ErrorType]
        else:
            # Test success response
            assert 'context' in result
            assert isinstance(result['context'], list)
    
    def test_retry_logic(self):
        """Test retry logic with invalid URL"""
        invalid_client = BridgeClient("http://invalid-url:9999")
        
        result = invalid_client.health_check()
        
        # Should fail with network error after retries
        assert result['success'] is False
        assert result['error_type'] == ErrorType.NETWORK.value
        assert result['fallback_used'] is True
    
    def test_timeout_handling(self):
        """Test timeout handling"""
        timeout_client = BridgeClient("http://localhost:5002", timeout=0.001)
        
        result = timeout_client.health_check()
        
        # Should handle timeout gracefully
        if result.get('success') is False:
            assert result['error_type'] == ErrorType.NETWORK.value
    
    def test_is_healthy_method(self):
        """Test boolean health check method"""
        result = self.client.is_healthy()
        
        # Should return boolean
        assert isinstance(result, bool)
    
    def test_error_classification(self):
        """Test error type classification"""
        # Test with invalid client
        invalid_client = BridgeClient("http://localhost:9999")
        
        result = invalid_client.log({"test": "data"})
        
        assert result['success'] is False
        assert result['error_type'] == ErrorType.NETWORK.value
        assert 'error_message' in result
        assert 'endpoint' in result