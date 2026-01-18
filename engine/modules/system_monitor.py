import threading
import time
import psutil
import GPUtil
import GPUtil
import logging

logger = logging.getLogger("engine.modules.system_monitor")

class SystemMonitor:
    def __init__(self, interval=2.0):
        self.interval = interval
        self.running = False
        self.thread = None
        self.current_stats = {
            "cpu": 0.0,
            "ram": 0.0,
            "gpu": None,
            "vram": None
        }

    def start(self):
        """Starts the monitoring thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            logger.info("System Monitor started.")

    def stop(self):
        """Stops the monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            logger.info("System Monitor stopped.")

    def _monitor_loop(self):
        """Background loop to update stats."""
        while self.running:
            try:
                self.update_stats()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(self.interval)

    def update_stats(self):
        """Updates the current statistics."""
        # CPU & RAM
        self.current_stats['cpu'] = psutil.cpu_percent(interval=None)
        self.current_stats['ram'] = psutil.virtual_memory().percent
        
        # GPU & VRAM
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                self.current_stats['gpu'] = gpu.load * 100
                self.current_stats['vram'] = gpu.memoryUtil * 100
            else:
                self.current_stats['gpu'] = None
                self.current_stats['vram'] = None
        except Exception:
            # Fallback if GPUtil fails or no Nvidia driver
            self.current_stats['gpu'] = None
            self.current_stats['vram'] = None

    def get_system_health(self):
        """Returns the latest system statistics."""
        return self.current_stats
    
    # Alias for test compatibility if needed, or we can update test to use get_system_health
    def get_stats(self):
        return self.get_system_health()
