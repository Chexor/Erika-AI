"""Test that all critical modules import correctly."""
import unittest


class TestModuleImports(unittest.TestCase):
    def test_engine_brain(self):
        from engine.brain import Brain
        self.assertIsNotNone(Brain)

    def test_engine_memory(self):
        from engine.memory import Memory, _is_valid_uuid
        self.assertIsNotNone(Memory)
        # Test UUID validation function
        self.assertTrue(_is_valid_uuid("12345678-1234-1234-1234-123456789abc"))
        self.assertFalse(_is_valid_uuid("invalid"))
        self.assertFalse(_is_valid_uuid("../../../etc/passwd"))

    def test_engine_network_router(self):
        from engine.network_router import BrainRouter
        self.assertIsNotNone(BrainRouter)

    def test_engine_singleton(self):
        from engine.singleton import WindowsSingleton
        self.assertIsNotNone(WindowsSingleton)

    def test_engine_logger(self):
        from engine.logger import configure_system_logging
        self.assertIsNotNone(configure_system_logging)

    def test_domain_reflection_service(self):
        from domain.subconscious.reflection_service import ReflectionService
        self.assertIsNotNone(ReflectionService)
        from engine.modules.system_monitor import SystemMonitor
        self.assertIsNotNone(SystemMonitor)

    def test_engine_modules_time_keeper(self):
        from engine.modules.time_keeper import TimeKeeper
        self.assertIsNotNone(TimeKeeper)

    def test_engine_modules_token_counter(self):
        from engine.modules.token_counter import TokenCounter
        self.assertIsNotNone(TokenCounter)

    def test_interface_controller(self):
        from interface.controller import Controller, MAX_INPUT_LENGTH, LLM_GENERATION_TIMEOUT
        self.assertIsNotNone(Controller)
        self.assertEqual(MAX_INPUT_LENGTH, 50000)
        self.assertEqual(LLM_GENERATION_TIMEOUT, 300)

    def test_interface_settings_ui(self):
        from interface.settings_ui import build_settings_modal, ALLOWED_HANDLERS, _safe_get_handler
        self.assertIsNotNone(build_settings_modal)
        self.assertIn('set_username', ALLOWED_HANDLERS)
        self.assertIn('set_context_window', ALLOWED_HANDLERS)

    def test_tools_speech_engine(self):
        from tools.speech_engine import SpeechEngine, TEMP_FILE_MAX_AGE
        self.assertIsNotNone(SpeechEngine)
        self.assertEqual(TEMP_FILE_MAX_AGE, 3600)


if __name__ == '__main__':
    unittest.main()
