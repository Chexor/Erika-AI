import unittest
import datetime
from unittest.mock import patch

try:
    from engine.modules.time_keeper import TimeKeeper
except ImportError:
    TimeKeeper = None


class TestCircadianLogic(unittest.TestCase):

    def test_import_exists(self):
        """Fail if TimeKeeper class is not implemented."""
        self.assertIsNotNone(TimeKeeper, "TimeKeeper class not found")

    def test_rollover_pre_5am(self):
        """Test that 2 AM counts as the previous day."""
        if not TimeKeeper:
            self.skipTest("No TimeKeeper")

        # Mock datetime to be 2026-01-19 02:00:00
        mock_now = datetime.datetime(2026, 1, 19, 2, 0, 0)

        with patch('engine.modules.time_keeper.datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_now

            logical_date = TimeKeeper.get_logical_date()
            expected_date = datetime.date(2026, 1, 18)

            self.assertEqual(logical_date, expected_date, "2AM should belong to previous day")

    def test_rollover_post_5am(self):
        """Test that 6 AM counts as the current day."""
        if not TimeKeeper:
            self.skipTest("No TimeKeeper")

        # Mock datetime to be 2026-01-19 06:00:00
        mock_now = datetime.datetime(2026, 1, 19, 6, 0, 0)

        with patch('engine.modules.time_keeper.datetime.datetime') as mock_dt:
            mock_dt.now.return_value = mock_now

            logical_date = TimeKeeper.get_logical_date()
            expected_date = datetime.date(2026, 1, 19)

            self.assertEqual(logical_date, expected_date, "6AM should belong to current day")

if __name__ == '__main__':
    unittest.main()
