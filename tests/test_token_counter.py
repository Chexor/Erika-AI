
import unittest
from engine.modules.token_counter import TokenCounter

class TestTokenCounter(unittest.TestCase):
    def setUp(self):
        self.counter = TokenCounter()

    def test_count_text(self):
        text = "Hello, world!"
        count = self.counter.count(text)
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)

    def test_count_messages(self):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        count = self.counter.count_messages(messages)
        self.assertIsInstance(count, int)
        self.assertGreater(count, 0)
        # Check that overhead is accounted for (simple check: it should be > than just content tokens)
        content_tokens = self.counter.count("You are a helpful assistant.") + self.counter.count("Hello!")
        self.assertGreater(count, content_tokens)

if __name__ == '__main__':
    unittest.main()
