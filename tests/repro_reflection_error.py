
import unittest
import datetime
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Import the service to test
from domain.subconscious.reflection_service import ReflectionService

class TestReflectionBug(unittest.IsolatedAsyncioTestCase):
    async def test_error_chunk_is_ignored(self):
        """
        Reproduce Bug: Brain yields {'error':...}, Service ignores it,
        saves empty file, and returns 'Completed'.
        """
        # 1. Setup Mocks
        mock_brain = MagicMock()
        mock_memory = MagicMock()
        mock_router = MagicMock()
        
        # Router says remote is online
        mock_router.status = {'remote': True}
        mock_router.REMOTE_BRAIN = 'http://fake:11434'
        mock_router.REMOTE_MODEL = 'fake-model'
        
        # Memory returns some chats
        mock_memory.get_chats_by_date.return_value = [{'messages': [{'role': 'user', 'content': 'hi'}]}]
        
        # Brain yields an error chunk instad of raising exception
        async def error_generator(*args, **kwargs):
            yield {"error": "Connection refused"}
            
        mock_brain.generate_response = error_generator
        
        # 2. Init Service
        service = ReflectionService(mock_brain, mock_memory, mock_router)
        service.output_dir = "tests/temp_reflections" # Sandbox
        os.makedirs(service.output_dir, exist_ok=True)
        
        # 3. Run
        # This SHOULD fail or return "Failed", but due to the bug it will likely return "Completed"
        status, content = await service.reflect_on_day(datetime.date(2025, 1, 1))
        
        print(f"\n[repro] Status: {status}")
        print(f"[repro] Content Length: {len(content) if content else 0}")
        
        # 4. Assertions - verifying the FIX
        # The service should now catch the error and return Failed
        self.assertEqual(status, "Failed", "Fix Verified: Service correctly reported failure!")
        self.assertIsNone(content, "Fix Verified: Content should be None")
        
        # Verify file was NOT created
        files = os.listdir(service.output_dir)
        self.assertEqual(len(files), 0, "Fix Verified: No corrupt files were created")
        
        # Cleanup
        os.rmdir(service.output_dir)

if __name__ == "__main__":
    unittest.main()
