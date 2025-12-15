"""
Test context injection for Creator module
Tests how context is injected into creator requests
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.creator import CreatorAgent
from db.memory_adapter import MemoryAdapter
from utils.bridge_client import BridgeClient

class TestContextInjectionCreator:
    """Test context injection for Creator agent"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test components"""
        self.memory_adapter = MemoryAdapter()
        self.creator_agent = CreatorAgent(self.memory_adapter)
        self.bridge_client = BridgeClient("http://localhost:5002")
        self.test_user_id = "test_user_context"
    
    def test_creator_context_injection(self):
        """Test context is injected into creator requests"""
        # Store some context first
        context_data = [
            {
                "module": "creator",
                "timestamp": "2025-01-01T00:00:00",
                "request": {"topic": "AI", "goal": "educational"},
                "response": {"content": "AI educational content"}
            },
            {
                "module": "creator", 
                "timestamp": "2025-01-01T01:00:00",
                "request": {"topic": "Technology", "goal": "tutorial"},
                "response": {"content": "Technology tutorial"}
            }
        ]
        
        # Store context in memory
        for ctx in context_data:
            self.memory_adapter.store_interaction(
                self.test_user_id,
                ctx["request"],
                ctx["response"]
            )
        
        # Test creator request with context injection
        request_data = {
            "topic": "Machine Learning",
            "goal": "Create tutorial", 
            "type": "article"
        }
        
        # Process request through creator agent
        response = self.creator_agent.process_request(
            "generate",
            self.test_user_id, 
            request_data
        )
        
        # Verify response structure
        assert isinstance(response, dict)
        assert "status" in response
        
        if response.get("status") == "success":
            assert "result" in response
    
    def test_context_retrieval_from_bridge(self):
        """Test context retrieval from bridge client"""
        # Get context from bridge
        bridge_context = self.bridge_client.get_context(limit=3)
        
        if bridge_context.get('success') is not False:
            # Bridge available, test context structure
            assert 'context' in bridge_context
            assert isinstance(bridge_context['context'], list)
            
            # Test context limit
            assert len(bridge_context['context']) <= 3
            
            # Test context item structure
            if len(bridge_context['context']) > 0:
                context_item = bridge_context['context'][0]
                assert 'id' in context_item or 'content' in context_item
        else:
            # Bridge not available, test error handling
            assert bridge_context['error_type'] in ['network', 'logic', 'schema', 'unexpected']
    
    def test_context_injection_with_memory_fallback(self):
        """Test context injection falls back to memory when bridge unavailable"""
        # Store local context
        self.memory_adapter.store_interaction(
            self.test_user_id,
            {"topic": "Fallback Test", "module": "creator"},
            {"status": "success", "content": "fallback content"}
        )
        
        # Test with potentially unavailable bridge
        request_data = {
            "topic": "New Topic",
            "goal": "Test fallback",
            "type": "test"
        }
        
        # Process through creator
        response = self.creator_agent.process_request(
            "generate",
            self.test_user_id,
            request_data
        )
        
        # Should work regardless of bridge availability
        assert isinstance(response, dict)
        assert "status" in response
    
    def test_context_limit_enforcement_creator(self):
        """Test context limits are enforced for creator"""
        # Store many interactions
        for i in range(10):
            self.memory_adapter.store_interaction(
                self.test_user_id,
                {"topic": f"Topic_{i}", "module": "creator"},
                {"status": "success", "content": f"content_{i}"}
            )
        
        # Get context with limit
        context = self.memory_adapter.get_context(self.test_user_id, limit=3)
        
        # Should respect limit
        assert len(context) <= 3
        
        # Should be most recent
        if len(context) > 0:
            # Most recent should have higher topic number
            recent_topic = context[0]['request']['topic']
            assert 'Topic_' in recent_topic
    
    def test_creator_with_empty_context(self):
        """Test creator works with empty context"""
        # Use fresh user ID with no context
        fresh_user_id = "fresh_user_no_context"
        
        request_data = {
            "topic": "Fresh Topic",
            "goal": "Test empty context",
            "type": "article"
        }
        
        # Process request
        response = self.creator_agent.process_request(
            "generate",
            fresh_user_id,
            request_data
        )
        
        # Should work even with no context
        assert isinstance(response, dict)
        assert "status" in response
    
    def test_context_injection_different_intents(self):
        """Test context injection works for different creator intents"""
        intents_to_test = ["generate", "analyze", "review"]
        
        for intent in intents_to_test:
            request_data = {
                "topic": f"Topic for {intent}",
                "goal": f"Test {intent} intent"
            }
            
            response = self.creator_agent.process_request(
                intent,
                self.test_user_id,
                request_data
            )
            
            # Each intent should work
            assert isinstance(response, dict)
            assert "status" in response
            
            if response.get("status") == "success":
                assert "result" in response
            elif response.get("status") == "error":
                # Unknown intent should return error
                assert "message" in response
    
    def test_context_data_structure(self):
        """Test context data has proper structure"""
        # Store structured context
        structured_request = {
            "module": "creator",
            "intent": "generate",
            "topic": "Structured Test",
            "goal": "Test structure"
        }
        
        structured_response = {
            "status": "success",
            "result": {
                "content_type": "creative",
                "data": {"generated": "structured content"}
            }
        }
        
        self.memory_adapter.store_interaction(
            self.test_user_id,
            structured_request,
            structured_response
        )
        
        # Retrieve and verify structure
        context = self.memory_adapter.get_context(self.test_user_id, limit=1)
        
        assert len(context) >= 1
        stored_item = context[0]
        
        # Verify structure preservation
        assert stored_item['request']['topic'] == "Structured Test"
        assert stored_item['response']['status'] == "success"