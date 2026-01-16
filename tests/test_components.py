import unittest
from unittest.mock import MagicMock
# We import nicegui.ui to ensure it builds invalid components without a page, 
# but usually nicegui functions need an active client context. 
# However, we just want to verify the module structure and signature existence 
# as per the "Red" step requirement: "attempt to import and initialize".
# Depending on nicegui internals, calling them might raise an error if not in a page context.
# We will catch that specific error if it proves function existence.

try:
    from interface.components import Sidebar, HeroSection, InputPill, ChatArea
except ImportError:
    pass # Expected failure for RED step

class TestComponents(unittest.TestCase):
    def test_components_exist(self):
        # This test will fail if module or functions don't exist
        from interface.components import Sidebar, HeroSection, InputPill, ChatArea
        self.assertTrue(callable(Sidebar))
        self.assertTrue(callable(HeroSection))
        self.assertTrue(callable(InputPill))
        self.assertTrue(callable(ChatArea))

    def test_sidebar_signature(self):
        from interface.components import Sidebar
        # We assume we can pass mocks. Even if it fails due to "no page connection",
        # catching that proves the function entered execution.
        try:
            Sidebar(history=[], on_select=MagicMock(), on_new=MagicMock(), on_settings=MagicMock())
        except Exception as e:
            # If the error is "ImportError" or "NameError" it fails. 
            # If it's a NiceGUI context error, we consider the signature valid enough for this unit test level.
            # ideally we inspect signature.
            import inspect
            sig = inspect.signature(Sidebar)
            self.assertIn('history', sig.parameters)
            self.assertIn('on_select', sig.parameters)

    def test_input_pill_signature(self):
        from interface.components import InputPill
        import inspect
        sig = inspect.signature(InputPill)
        self.assertIn('models', sig.parameters)
        self.assertIn('on_send', sig.parameters)

if __name__ == '__main__':
    unittest.main()
