import unittest
import os
import sys
import shutil
import json
import datetime
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interface.state import AppState
from interface.controller import ErikaController
from core.settings import SettingsManager
from core.memory import MemoryManager

class TestHydration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Setup temporary directories
        self.test_dir = os.path.join(os.path.dirname(__file__), "temp_hydration_test")
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Mocks
        self.settings = MagicMock(spec=SettingsManager)
        self.memory = MemoryManager(self.settings, base_path=self.test_dir)
        self.state = AppState()
        
        # We need to make sure sidebar_history exists in state (it might fail if not added yet - RED)
        if not hasattr(self.state, 'sidebar_history'):
            # If not present, we can mock it or let it fail if the controller expects it
            # But for the test setup, we might need to monkeypatch or just expect AttributeError
            pass

        self.controller = ErikaController(self.state, self.settings, self.memory)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_dummy_chat(self, chat_id, days_ago=0):
        timestamp = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)).isoformat()
        data = {
            "id": chat_id,
            "created_at": timestamp,
            "messages": [{"role": "user", "content": f"Message from {days_ago} days ago"}]
        }
        with open(os.path.join(self.test_dir, f"{chat_id}.json"), 'w') as f:
            json.dump(data, f)

    async def test_load_all_chats(self):
        # Create 3 dummy chats
        self._create_dummy_chat("chat1", days_ago=0) # Today
        self._create_dummy_chat("chat2", days_ago=1) # Yesterday
        self._create_dummy_chat("chat3", days_ago=2) # Older

        # Call load_all_chats
        # This method might not exist yet (RED)
        if not hasattr(self.controller, 'load_all_chats'):
            self.fail("controller.load_all_chats not implemented")

        await self.controller.load_all_chats()

        # Verify state.sidebar_history
        if not hasattr(self.state, 'sidebar_history'):
             self.fail("state.sidebar_history not implemented")
             
        self.assertEqual(len(self.state.sidebar_history), 3)
        
        # Verify order (Newest first)
        self.assertEqual(self.state.sidebar_history[0]['id'], "chat1")
        self.assertEqual(self.state.sidebar_history[1]['id'], "chat2")
        self.assertEqual(self.state.sidebar_history[2]['id'], "chat3")

if __name__ == '__main__':
    unittest.main()
