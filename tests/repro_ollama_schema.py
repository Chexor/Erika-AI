import unittest
from unittest.mock import patch, MagicMock
from core.brain import Brain
from core.settings import SettingsManager

class TestOllamaSchema(unittest.TestCase):
    def setUp(self):
        self.settings = MagicMock(spec=SettingsManager)
        self.brain = Brain(self.settings)

    @patch('core.brain.ollama')
    def test_list_response_structure(self, mock_ollama):
        # Current implementation expects: {'models': [{'name': '...'}]}
        # Actual Ollama might return: {'models': [{'model': '...'}]} or similar
        # Or maybe it returns a list directly?
        # The error "KeyError: 'name'" confirms it returns a dict, but 'name' key is missing inside the models list items.
        
        # Let's mock what we SUSPECT is the real response (based on recent Ollama API changes)
        # Recent Ollama often uses 'model' instead of 'name' or nested 'details'.
        # Or maybe the object attribute access?
        # Let's try to verify if adaptation works if we simulate the "new" schema.
        
        mock_ollama.list.return_value = {
            'models': [
                {'model': 'llama3:latest', 'modified_at': '...'},
                {'model': 'mistral:latest', 'modified_at': '...'}
            ]
        }
        
        # If code is broken, this returns [] or logs error
        models = self.brain.get_available_models()
        
        # We want to see if it extracted them
        self.assertEqual(models, ['llama3:latest', 'mistral:latest'])

if __name__ == '__main__':
    unittest.main()
