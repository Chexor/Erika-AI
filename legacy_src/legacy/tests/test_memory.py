import unittest
import os
import json
import shutil
import uuid
from core.memory import MemoryManager
from core.settings import SettingsManager

class TestMemory(unittest.TestCase):
    def setUp(self):
        # Setup clean test environment
        self.test_dir = os.path.join(os.getcwd(), 'tests_temp_memory')
        self.chats_dir = os.path.join(self.test_dir, 'chats')
        self.config_dir = os.path.join(self.test_dir, 'config')
        
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Initialize Settings (needed for MemoryManager if tight coupling, 
        # but broadly we just need to pass the paths or rely on defaults.
        # However, the requirement says "Use SettingsManager to determine storage preferences".
        # For testing, we might need to inject the path or patch settings.
        # Assuming MemoryManager takes a root path or we patch the default location.
        # Let's assume MemoryManager constructor accepts a `chats_path` or we patch the global constant.
        # To adhere strictly to "Use SettingsManager", `MemoryManager` probably takes `SettingsManager` as a dependency.
        
        self.settings = SettingsManager(
            system_path=os.path.join(self.config_dir, 'system.json'),
            user_path=os.path.join(self.config_dir, 'user.json')
        )
        
        # We will inject the chats directory via checking if MemoryManager allows override,
        # or we assume it uses a relative 'chats' folder. 
        # For test isolation, we want it in self.chats_dir.
        # Let's assume constructor args: MemoryManager(settings_manager, base_path=...)
        self.memory = MemoryManager(self.settings, base_path=self.chats_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization_creates_directory(self):
        self.assertTrue(os.path.exists(self.chats_dir), "Chats directory not created on instantiation")

    def test_create_chat(self):
        chat_id = self.memory.create_chat()
        self.assertIsNotNone(chat_id)
        
        # Verify file creation
        file_path = os.path.join(self.chats_dir, f"{chat_id}.json")
        self.assertTrue(os.path.exists(file_path), "Chat file not created")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data['id'], chat_id)
            self.assertEqual(data['messages'], [])
            self.assertIn('created_at', data)

    def test_save_message(self):
        chat_id = self.memory.create_chat()
        self.memory.save_message(chat_id, "user", "Hello Erika")
        
        chat_data = self.memory.get_chat(chat_id)
        messages = chat_data['messages']
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[0]['content'], 'Hello Erika')

    def test_get_chat_not_found(self):
        # Depending on implementation, might return None or raise
        # Let's assume return None for safety, or check if specific exception needed.
        # Prompt says "Should retrieve the full chat object".
        result = self.memory.get_chat("non_existent_id")
        self.assertIsNone(result)

    def test_list_all_chats(self):
        id1 = self.memory.create_chat()
        self.memory.save_message(id1, "user", "Msg 1")
        
        id2 = self.memory.create_chat()
        
        chats_list = self.memory.list_all_chats()
        
        # Should create a list of metadata dicts
        self.assertTrue(len(chats_list) >= 2)
        
        ids = [c['id'] for c in chats_list]
        self.assertIn(id1, ids)
        self.assertIn(id2, ids)

if __name__ == '__main__':
    unittest.main()
