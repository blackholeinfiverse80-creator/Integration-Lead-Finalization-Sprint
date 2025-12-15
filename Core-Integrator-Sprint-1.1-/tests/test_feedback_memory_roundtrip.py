"""
Test feedback memory roundtrip functionality
Tests the complete flow: feedback -> memory storage -> retrieval
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.bridge_client import BridgeClient
from db.memory_adapter import MemoryAdapter

class TestFeedbackMemoryRoundtrip:
    """Test feedback storage and retrieval roundtrip"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test components"""
        self.bridge_client = BridgeClient("http://localhost:5002")
        self.memory_adapter = MemoryAdapter()
        self.test_user_id = "test_user_feedback"
    
    def test_feedback_to_bridge_storage(self):
        """Test feedback sent to bridge and stored"""
        feedback_data = {
            "user_id": self.test_user_id,
            "rating": 4,
            "comment": "Good response",
            "session_id": "session_123"
        }
        
        # Send feedback to bridge
        bridge_result = self.bridge_client.feedback(feedback_data)
        
        if bridge_result.get('success') is not False:
            # Bridge accepted feedback
            assert bridge_result.get('status') == 'feedback_received'
            assert 'id' in bridge_result
        else:
            # Bridge not available, test error handling
            assert bridge_result['error_type'] in ['network', 'logic', 'schema', 'unexpected']
    
    def test_memory_storage_roundtrip(self):
        """Test memory storage and retrieval"""
        # Store interaction in memory
        request_data = {
            "module": "creator",
            "intent": "generate",
            "data": {"topic": "test", "goal": "test"}
        }
        
        response_data = {
            "status": "success",
            "result": {"content": "test content"}
        }
        
        # Store interaction
        self.memory_adapter.store_interaction(
            self.test_user_id, 
            request_data, 
            response_data
        )
        
        # Retrieve context
        context = self.memory_adapter.get_context(self.test_user_id, limit=1)
        
        # Verify roundtrip
        assert len(context) >= 1
        stored_interaction = context[0]
        assert stored_interaction['request'] == request_data
        assert stored_interaction['response'] == response_data
    
    def test_feedback_memory_integration(self):
        """Test feedback affects memory storage"""
        # Create initial interaction
        request_data = {
            "module": "creator", 
            "intent": "generate",
            "feedback_test": True
        }
        
        response_data = {
            "status": "success",
            "content": "feedback test content"
        }
        
        # Store interaction
        self.memory_adapter.store_interaction(
            self.test_user_id,
            request_data,
            response_data
        )
        
        # Send feedback through bridge
        feedback_data = {
            "user_id": self.test_user_id,
            "rating": 5,
            "interaction_type": "creator_generate"
        }
        
        bridge_result = self.bridge_client.feedback(feedback_data)
        
        # Verify feedback was processed (success or proper error handling)
        if bridge_result.get('success') is not False:
            assert bridge_result.get('status') == 'feedback_received'
        else:
            assert 'error_type' in bridge_result
        
        # Verify memory still accessible
        context = self.memory_adapter.get_context(self.test_user_id)
        assert len(context) >= 1
    
    def test_memory_limit_enforcement(self):
        """Test memory limits are enforced (5 per module)"""
        # Store multiple interactions
        for i in range(7):  # More than limit of 5
            request_data = {
                "module": "creator",
                "intent": "generate", 
                "iteration": i
            }
            
            response_data = {
                "status": "success",
                "content": f"content_{i}"
            }
            
            self.memory_adapter.store_interaction(
                self.test_user_id,
                request_data, 
                response_data
            )
        
        # Retrieve context
        context = self.memory_adapter.get_context(self.test_user_id, limit=10)
        
        # Should respect limit (5 or less recent items)
        assert len(context) <= 5
        
        # Should be most recent items
        if len(context) > 0:
            latest_item = context[0]
            assert latest_item['request']['iteration'] >= 2  # Recent iterations
    
    def test_context_warm_limit(self):
        """Test warm context limit (3 items)"""
        # Store interactions
        for i in range(5):
            self.memory_adapter.store_interaction(
                self.test_user_id,
                {"module": "creator", "warm_test": i},
                {"status": "success", "content": f"warm_{i}"}
            )
        
        # Get warm context (limit 3)
        warm_context = self.memory_adapter.get_context(self.test_user_id, limit=3)
        
        # Should return exactly 3 or fewer items
        assert len(warm_context) <= 3
    
    def test_user_history_retrieval(self):
        """Test user history retrieval"""
        # Store interaction
        self.memory_adapter.store_interaction(
            self.test_user_id,
            {"module": "creator", "history_test": True},
            {"status": "success", "history_content": True}
        )
        
        # Get user history
        history = self.memory_adapter.get_user_history(self.test_user_id)
        
        # Verify history structure
        assert isinstance(history, list)
        
        if len(history) > 0:
            history_item = history[0]
            assert 'timestamp' in history_item or 'request' in history_item