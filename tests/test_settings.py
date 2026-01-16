import unittest
import os
import json
import shutil
from core.settings import SettingsManager

class TestSettings(unittest.TestCase):
    def setUp(self):
        # Setup clean test environment
        self.test_dir = os.path.join(os.getcwd(), 'tests_temp_config')
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # We don't create the dir here to test that manager creates it
        
        self.system_path = os.path.join(self.test_dir, 'system.json')
        self.user_path = os.path.join(self.test_dir, 'user.json')
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_initialization_creates_directory(self):
        SettingsManager(system_path=self.system_path, user_path=self.user_path)
        self.assertTrue(os.path.exists(self.test_dir), "Config directory not created on instantiation")

    def test_get_set_system_error(self):
        """System config should be read-only via set method or just fail if we try to write? 
        The prompt says: 'Implement ... set(file_type, key, value)'.
        Usually system is read-only, but let's see if the user implies we can write to it.
        'write to a temporary file, then rename/replace' implies writing is possible.
        Let's assume we CAN write to system if strict mode allows, or verify behavior.
        The prompt asks to test 'disk persistence'.
        """
        settings = SettingsManager(system_path=self.system_path, user_path=self.user_path)
        
        # Test Set/Get System
        settings.set('system', 'version', '2.0')
        self.assertEqual(settings.get('system', 'version'), '2.0')
        
        # Verify persistence
        with open(self.system_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data.get('version'), '2.0')

    def test_get_set_user(self):
        settings = SettingsManager(system_path=self.system_path, user_path=self.user_path)
        
        settings.set('user', 'theme', 'solarized')
        self.assertEqual(settings.get('user', 'theme'), 'solarized')
        
        with open(self.user_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data.get('theme'), 'solarized')

    def test_invalid_file_type(self):
        settings = SettingsManager(system_path=self.system_path, user_path=self.user_path)
        with self.assertRaises(ValueError):
            settings.set('invalid_type', 'key', 'value')
        with self.assertRaises(ValueError):
            settings.get('invalid_type', 'key')

    def test_atomic_write_simulation(self):
        """Hard to test atomic write properly without race conditions, 
        but we can check if a .tmp file ever lingers or if the file is valid json."""
        settings = SettingsManager(system_path=self.system_path, user_path=self.user_path)
        settings.set('user', 'atomic_key', 'atomic_value')
        
        # Verify valid JSON
        with open(self.user_path, 'r') as f:
            content = json.load(f)
            self.assertEqual(content['atomic_key'], 'atomic_value')
            
        # Ensure no tmp file remains (assuming implementation uses .tmp suffix)
        self.assertFalse(os.path.exists(self.user_path + ".tmp"))

if __name__ == '__main__':
    unittest.main()
