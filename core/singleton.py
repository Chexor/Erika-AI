import os
import sys
import tempfile
from core.logger import setup_logger

logger = setup_logger("CORE.Singleton")

class SingletonLock:
    def __init__(self, app_name="erika_ai"):
        self.lock_file_path = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.lock_file = None
        
    def acquire(self):
        """
        Acquires an exclusive lock. Returns True if successful, False otherwise.
        """
        try:
            # Open the file in Append mode (create if not exists)
            self.lock_file = open(self.lock_file_path, 'w')
            
            # Windows-specific locking
            if os.name == 'nt':
                import msvcrt
                # Try to lock the first byte of the file
                # LOCK_EX: Exclusive lock
                # LOCK_NB: Non-blocking
                msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.lockf(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                
            # Write PID for debugging
            self.lock_file.write(str(os.getpid()))
            self.lock_file.flush()
            
            logger.info(f"Singleton lock acquired on {self.lock_file_path}")
            return True
            
        except (IOError, BlockingIOError, PermissionError) as e:
            logger.warning(f"Could not acquire singleton lock: {e}")
            if self.lock_file:
                try:
                    self.lock_file.close()
                except:
                    pass
                self.lock_file = None
            return False
            
    def release(self):
        """
        Releases the lock and closes the file.
        """
        if self.lock_file:
            try:
                # Truncate/Cleanup?
                # On Windows, closing releases the lock usually, but explicit unlock is safer if we keep file open.
                # Here we just close it.
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(self.lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.lockf(self.lock_file, fcntl.LOCK_UN)
                    
                self.lock_file.close()
                # We don't delete the file, so race conditions are minimized? 
                # Or we can delete it. 
                # Code says "Ensure the lock file is automatically deleted even if the app crashes" -> REFACTOR step.
                # For now, implemented basic locking.
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")
            finally:
                self.lock_file = None
                logger.info("Singleton lock released.")
