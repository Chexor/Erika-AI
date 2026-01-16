import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from interface.state import AppState
from interface.controller import ErikaController
from core.brain import Brain
from core.memory import MemoryManager
from core.settings import SettingsManager

class TestController(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_settings = MagicMock(spec=SettingsManager)
        self.mock_memory = MagicMock(spec=MemoryManager)
        self.mock_brain = MagicMock(spec=Brain)
        
        # State
        self.state = AppState()
        
        # We need to patch the constructor or inject dependencies if the Controller supports it.
        # Assuming Controller(state, settings=..., memory=..., brain=...) for testability.
        # If it initializes them internally, we must patch the classes.
        
    @patch('interface.controller.Brain')
    @patch('interface.controller.MemoryManager')
    @patch('interface.controller.SettingsManager')
    def test_initialization(self, MockSettings, MockMemory, MockBrain):
        # Setup returns
        MockSettings.return_value = self.mock_settings
        MockMemory.return_value = self.mock_memory
        MockBrain.return_value = self.mock_brain
        
        controller = ErikaController(self.state)
        
        self.assertIsNotNone(controller.brain)
        self.assertIsNotNone(controller.memory)
        self.assertIsNotNone(controller.settings)
        # Check initial state values from settings if applicable?
        pass

    async def async_handle_send_test(self):
        # This helper is needed because handle_send is likely async for streaming
        pass

    @patch('interface.controller.Brain')
    @patch('interface.controller.MemoryManager')
    @patch('interface.controller.SettingsManager')
    def test_handle_send_logic(self, MockSettings, MockMemory, MockBrain):
        # Setup
        MockBrain.return_value = self.mock_brain
        # Mock think_stream
        self.mock_brain.think_stream.return_value = iter(["Hello", " World"])
        
        controller = ErikaController(self.state)
        # Replace internal instances with ours to be sure
        controller.brain = self.mock_brain
        controller.memory = self.mock_memory
        
        # Action
        # Note: If handle_send is async, we need to run it. 
        # Requirement says "retrieve a stream ... update as chunks arrive".
        # This implies it might be blocking or async. 
        # Usually NiceGUI handlers can be async. Let's assume sync for simplest TDD unless forced.
        # "Inference Streaming" usually requires async to yield to UI loop.
        
        # Let's assume handle_send is async.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
             loop.run_until_complete(controller.handle_send("Hi Erika"))
        finally:
             loop.close()
        
        # Assertions
        # 1. State updated
        self.assertEqual(len(self.state.messages), 2, "Should have User + Assistant messages")
        self.assertEqual(self.state.messages[0]['content'], "Hi Erika")
        self.assertEqual(self.state.messages[1]['content'], "Hello World")
        self.assertEqual(self.state.messages[1]['role'], "assistant")
        
        # 2. Brain called
        self.mock_brain.think_stream.assert_called_once()
        
        # 3. Memory saved
        self.mock_memory.save_message.assert_called() # Should be called for user and assistant

if __name__ == '__main__':
    unittest.main()
