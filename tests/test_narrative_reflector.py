
import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock, patch

# Update Import
try:
    from domain.subconscious.reflection_service import ReflectionService
except ImportError:
    ReflectionService = None

class TestNarrativeReflector(unittest.IsolatedAsyncioTestCase):
    
    async def test_import_exists(self):
        self.assertIsNotNone(ReflectionService, "ReflectionService class not found")

    async def test_generate_prompt_content(self):
        """Verify prompt contains required structure."""
        if not ReflectionService: self.skipTest("No ReflectionService")
        
        service = ReflectionService(brain=MagicMock(), memory=MagicMock(), router=MagicMock())
        transcript = "[10:00] User: Hello\n[10:01] Erika: Hi Tim"
        
        prompt = service._generate_prompt(transcript)
        
        # New structure checks
        self.assertIn("The Pulse", prompt)
        self.assertIn("Hard Facts", prompt)

    async def test_reflect_call_params(self):
        """Verify ReflectionService calls brain correctly."""
        if not ReflectionService: self.skipTest("No ReflectionService")
        
        mock_router = MagicMock()
        mock_router.status = {'remote': True}
        mock_router.REMOTE_BRAIN = "http://remote:11434"
        mock_router.REMOTE_MODEL = "gemma2:9b"
        
        mock_brain = MagicMock()
        async def mock_gen(*args, **kwargs):
            yield {'message': {'content': 'Reflection'}}
        mock_brain.generate_response = MagicMock(side_effect=mock_gen)
        
        mock_memory = MagicMock()
        mock_memory.get_chats_by_date.return_value = [{'messages': [{'role':'user', 'content':'hi'}]}]
        
        service = ReflectionService(brain=mock_brain, memory=mock_memory, router=mock_router)

        # Mock writing file to avoid IO
        with patch('builtins.open', unittest.mock.mock_open()):
             status, content = await service.reflect_on_day(datetime.date(2026, 1, 18))
        
        self.assertEqual(status, "Completed")
        self.assertEqual(content, "Reflection")
        
        mock_brain.generate_response.assert_called()
