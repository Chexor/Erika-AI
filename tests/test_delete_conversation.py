import unittest
import os
import shutil
import json
import uuid
from engine.memory import Memory


class TestDeleteConversation(unittest.TestCase):
    def setUp(self):
        # Setup a test directory for memory
        self.test_dir = 'test_erika_memory'
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_delete_existing_chat(self):
        chat_dir = os.path.join(self.test_dir, 'chats')
        mem = Memory(base_path=chat_dir)

        # Use valid UUID format for chat_id (security requirement)
        chat_id = str(uuid.uuid4())
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

        # Use valid UUID format but non-existent
        non_existent_id = str(uuid.uuid4())
        result = mem.delete_chat(non_existent_id)
        self.assertFalse(result)

    def test_delete_invalid_chat_id_rejected(self):
        """Test that invalid chat IDs are rejected for security."""
        chat_dir = os.path.join(self.test_dir, 'chats')
        mem = Memory(base_path=chat_dir)

        # Path traversal attempt should be rejected
        result = mem.delete_chat("../../../etc/passwd")
        self.assertFalse(result)

        # Non-UUID format should be rejected
        result = mem.delete_chat("invalid_id")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
