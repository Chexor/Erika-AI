
import datetime

class TimeKeeper:
    DAY_ROLLOVER_HOUR = 5

    @staticmethod
    def get_date_from_datetime(dt: datetime.datetime) -> datetime.date:
        """Converts a specific datetime to its logical circadian date."""
        if dt.tzinfo is not None:
            dt = dt.astimezone()
        if dt.hour < TimeKeeper.DAY_ROLLOVER_HOUR:
            return dt.date() - datetime.timedelta(days=1)
        else:
            return dt.date()

    @staticmethod
    def get_logical_date() -> datetime.date:
        """
        Returns the logical date based on the circadian clock.
        Rollover happens at 5:00 AM.
        """
        now = datetime.datetime.now()
        if now.tzinfo is not None:
            now = now.astimezone()
        return TimeKeeper.get_date_from_datetime(now)
