import os
import tempfile
import msvcrt
import logging

logger = logging.getLogger("ENGINE.Singleton")


class WindowsSingleton:
    def __init__(self):
        self.lockfile = os.path.join(tempfile.gettempdir(), ".erika.lock")
        self.fp = None

    def acquire(self) -> bool:
        """
        Acquire the lock. Returns True on success, False if already locked.
        """
        try:
            # Open for reading/writing, creating if needed
            self.fp = open(self.lockfile, 'w')

            # Try to lock (non-blocking)
            msvcrt.locking(self.fp.fileno(), msvcrt.LK_NBLCK, 1)

            self.fp.write(str(os.getpid()))
            self.fp.flush()
            return True
        except (IOError, PermissionError, OSError) as e:
            # Already locked or permission denied
            logger.debug(f"Singleton: Lock acquisition failed: {e}")
            if self.fp:
                try:
                    self.fp.close()
                except OSError:
                    pass
                self.fp = None
            return False

    def release(self):
        """Release the lock."""
        if self.fp:
            try:
                # Unlock
                self.fp.seek(0)
                msvcrt.locking(self.fp.fileno(), msvcrt.LK_UNLCK, 1)
            except (IOError, OSError) as e:
                logger.debug(f"Singleton: Error unlocking: {e}")
            finally:
                try:
                    self.fp.close()
                except OSError:
                    pass
                try:
                    os.remove(self.lockfile)
                except OSError as e:
                    logger.debug(f"Singleton: Error removing lock file: {e}")
                self.fp = None
