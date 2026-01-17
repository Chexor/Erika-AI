import time
import sys
import signal
import threading
from core.logger import setup_logger, setup_global_capture
from core.singleton import SingletonLock

# Setup Logging
setup_global_capture()
logger = setup_logger("ENGINE.Bootstrapper")

# Global State
running = True
lock = None

def shutdown_handler(signum, frame):
    """Handle shutdown signals."""
    global running
    logger.info(f"Signal {signum} received. Shutting down...")
    running = False

def main():
    global lock, running
    
    logger.info("Engine: Initializing background service...")
    
    # 1. Acquire Singleton Lock
    lock = SingletonLock()
    if not lock.acquire():
        logger.error("Engine already running. Exiting.")
        print("Engine already running.")
        sys.exit(1)
        
    logger.info("Engine: Singleton lock acquired.")
    
    # 2. Setup Signal Handlers
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # 3. Main Engine Loop
    logger.info("Engine: Entering persistent loop.")
    try:
        while running:
            # Placeholder for core logic heartbeat
            time.sleep(1)
    except Exception as e:
        logger.error(f"Engine crashed: {e}")
    finally:
        logger.info("Engine: Cleaning up...")
        try:
            lock.release()
            logger.info("Engine: Lock released.")
        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
        logger.info("Engine: Shutdown complete.")

if __name__ == "__main__":
    main()
