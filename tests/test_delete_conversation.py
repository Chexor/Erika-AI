
import unittest
import os
import shutil
import json
from engine.memory import Memory

class TestDeleteConversation(unittest.TestCase):
    def setUp(self):
        # Setup a test directory for memory
        self.test_dir = 'test_erika_memory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Initialize Memory with test config/paths if possible
        # Since Memory uses hardcoded paths or config, we might need to mock or subclass
        # Looking at memory.py, it takes no args in __init__ but uses internal paths?
        # Let's inspect memory.py content first (already requested).
        # Assuming we can instantiate it and it uses a standard path, 
        # OR we modify Memory to accept a base_path for testing.
        # For now, let's assume standard instantiation and we might need to patch it.
        pass

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_existing_chat(self):
        chat_dir = os.path.join(self.test_dir, 'chats')
        mem = Memory(base_path=chat_dir)
        
        chat_id = "test_chat_1"
        file_path = os.path.join(chat_dir, f"{chat_id}.json")
        with open(file_path, 'w') as f:
            json.dump({"id": chat_id, "messages": []}, f)
            
        self.assertTrue(os.path.exists(file_path))
        
        result = mem.delete_chat(chat_id)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(file_path))

    def test_delete_non_existent_chat(self):
        chat_dir = os.path.join(self.test_dir, 'chats')
        mem = Memory(base_path=chat_dir)
        
        result = mem.delete_chat("non_existent_id")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
