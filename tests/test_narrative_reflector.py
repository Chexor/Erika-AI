
import unittest
import datetime
from unittest.mock import MagicMock, AsyncMock, patch

try:
    from engine.modules.reflector import Reflector
except ImportError:
    Reflector = None

class TestNarrativeReflector(unittest.IsolatedAsyncioTestCase):
    
    async def test_import_exists(self):
        self.assertIsNotNone(Reflector, "Reflector class not found")

    async def test_generate_prompt_content(self):
        """Verify prompt contains required emotional context."""
        if not Reflector: self.skipTest("No Reflector")
        
        reflector = Reflector(brain=MagicMock(), memory=MagicMock(), router=MagicMock())
        transcript = "[10:00] User: Hello\n[10:01] Erika: Hi Tim"
        
        prompt = reflector._generate_prompt(transcript)
        
        self.assertIn("emotional arc", prompt)
        self.assertIn("first person", prompt)
        self.assertIn("Morning Perspective", prompt)

    async def test_reflect_call_params(self):
        """Verify Reflector calls brain with correct remote model."""
        if not Reflector: self.skipTest("No Reflector")
        
        mock_router = MagicMock()
        mock_router.status = {'remote': True}
        mock_router.REMOTE_BRAIN = "http://remote:11434"
        mock_router.REMOTE_MODEL = "gemma2:9b"
        
        mock_brain = MagicMock()
        # Mock generate_response to be an async iterable
        async def mock_gen(*args, **kwargs):
            yield {'message': {'content': 'Reflection'}}
        mock_brain.generate_response = MagicMock(side_effect=mock_gen)
        
        mock_memory = MagicMock()
        mock_memory.get_chats_by_date.return_value = [{'messages': [{'role':'user', 'content':'hi'}]}]
        
        reflector = Reflector(brain=mock_brain, memory=mock_memory, router=mock_router)

        await reflector.reflect_on_day(datetime.date(2026, 1, 18))
        
        # Check call arguments
        mock_brain.generate_response.assert_called()
        call_kwargs = mock_brain.generate_response.call_args.kwargs
        self.assertEqual(call_kwargs['model'], "gemma2:9b")
        self.assertEqual(call_kwargs['host'], "http://remote:11434")

if __name__ == '__main__':
    unittest.main()
