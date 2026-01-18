import unittest
import sys
import os
import shutil
import tempfile
import json
import asyncio

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEngineMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_memory_crud(self):
        """Test create and read chats."""
        try:
            from engine.memory import Memory
        except ImportError:
            self.fail("engine.memory module not found (RED)")

        memory = Memory(base_path=self.test_dir)

        # Create returns a dict with id, created_at, messages
        chat_data = memory.create_chat()
        self.assertIsInstance(chat_data, dict)
        self.assertIn('id', chat_data)
        chat_id = chat_data['id']

        # Add a message and save (create_chat doesn't persist to disk)
        chat_data['messages'].append({"role": "user", "content": "Hello"})
        memory.save_chat(chat_id, chat_data)

        # Read back
        loaded = memory.get_chat(chat_id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded['messages'][0]['content'], "Hello")

if __name__ == '__main__':
    unittest.main()
