import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEngineBrain(unittest.IsolatedAsyncioTestCase):
    async def test_brain_initialization_and_check(self):
        """Test Brain initialization and connection check."""
        # Mock ollama client
        with patch('engine.brain.AsyncClient') as mock_client:
            # Setup mock
            mock_instance = mock_client.return_value
            # list is an async method, so it should return an awaitable. 
            # AsyncMock handles this if configured, but explicit is safer for return_value.
            mock_instance.list = AsyncMock(return_value={'models': [{'name': 'llama3'}]})
            
            # Check module import
            try:
                 from engine.brain import Brain
            except ImportError:
                self.fail("engine.brain module not found (RED)")
                
            brain = Brain()
            status = await brain.check_connection()
            self.assertTrue(status)
            
            # Test failure case
            mock_instance.list.side_effect = Exception("Connection refused")
            status = await brain.check_connection()
            self.assertFalse(status)

if __name__ == '__main__':
    unittest.main()
