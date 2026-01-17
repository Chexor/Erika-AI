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
        
        # Create
        chat_id = memory.create_chat()
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, f"{chat_id}.json")))
        
        # Write message (simulate controller update)
        chat_data = memory.get_chat(chat_id)
        chat_data['messages'].append({"role": "user", "content": "Hello"})
        memory.save_chat(chat_id, chat_data)
        
        # Read back
        loaded = memory.get_chat(chat_id)
        self.assertEqual(loaded['messages'][0]['content'], "Hello")

if __name__ == '__main__':
    unittest.main()
