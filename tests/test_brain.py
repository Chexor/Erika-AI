import unittest
from unittest.mock import patch, MagicMock
from core.settings import SettingsManager
from core.brain import Brain

class TestBrain(unittest.TestCase):
    def setUp(self):
        self.settings_mock = MagicMock(spec=SettingsManager)
        # Mock settings.get to return predictable values
        self.settings_mock.get.side_effect = lambda file_type, key, default=None: default
        
        # We don't need to reload brain here if we patch properly
        self.brain = Brain(self.settings_mock)

    @patch('core.brain.ollama')
    def test_get_available_models(self, mock_ollama):
        # Setup mock behavior on the passed mock object
        mock_ollama.list.return_value = {
            'models': [
                {'name': 'llama3:latest'},
                {'name': 'mistral:latest'}
            ]
        }
        
        models = self.brain.get_available_models()
        self.assertIn('llama3:latest', models)
        self.assertIn('mistral:latest', models)

    @patch('core.brain.ollama')
    def test_think_stream(self, mock_ollama):
        # Mock the chat stream
        # chat returns an iterator (generator)
        mock_ollama.chat.return_value = iter([
            {'message': {'content': 'Hello'}},
            {'message': {'content': ' World'}}
        ])
        
        messages = [{'role': 'user', 'content': 'Hi'}]
        chunks = list(self.brain.think_stream(messages))
        
        self.assertEqual(chunks, ['Hello', ' World'])
        mock_ollama.chat.assert_called_once()
        # Verify stream=True was passed
        kwargs = mock_ollama.chat.call_args.kwargs
        self.assertTrue(kwargs.get('stream'))

    @patch('core.brain.ollama')
    def test_check_connection_success(self, mock_ollama):
        mock_ollama.list.return_value = {'models': []}
        self.assertTrue(self.brain.check_connection())

    @patch('core.brain.ollama')
    def test_check_connection_failure(self, mock_ollama):
        mock_ollama.list.side_effect = Exception("Connection refused")
        self.assertFalse(self.brain.check_connection())

if __name__ == '__main__':
    unittest.main()
