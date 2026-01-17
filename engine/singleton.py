import os
import sys
import tempfile
import msvcrt

class WindowsSingleton:
    def __init__(self):
        self.lockfile = os.path.join(tempfile.gettempdir(), ".erika.lock")
        self.fp = None

    def acquire(self) -> bool:
        """
        Acquire the lock. Returns True on success, False if already locked.
        """
        try:
            if os.path.exists(self.lockfile):
                # If file exists, try to open it r+ to lock
                pass
            
            # Open for reading/writing, creating if needed
            self.fp = open(self.lockfile, 'w')
            
            # Try to lock
            # LK_NBL: Non-blocking lock
            # LK_NBRL: Non-blocking byte range lock
            msvcrt.locking(self.fp.fileno(), msvcrt.LK_NBLCK, 1)
            
            self.fp.write(str(os.getpid()))
            self.fp.flush()
            return True
        except (IOError, PermissionError):
            # Already locked
            if self.fp:
                self.fp.close()
                self.fp = None
            return False

    def release(self):
        """Release the lock."""
        if self.fp:
            try:
                # Unlock
                self.fp.seek(0)
                msvcrt.locking(self.fp.fileno(), msvcrt.LK_UNLCK, 1)
            except Exception:
                pass
            finally:
                self.fp.close()
                try:
                    os.remove(self.lockfile)
                except Exception:
                    pass
                self.fp = None
