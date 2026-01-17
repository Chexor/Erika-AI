import GPUtil
import platform
import sys

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")

try:
    gpus = GPUtil.getGPUs()
    print(f"GPUs Detected: {len(gpus)}")
    for i, gpu in enumerate(gpus):
        print(f"GPU {i}: {gpu.name}")
        print(f"  Load: {gpu.load * 100}%")
        print(f"  Memory: {gpu.memoryUtil * 100}%")
        print(f"  Total Mem: {gpu.memoryTotal}MB")
except Exception as e:
    print(f"Error getting GPUs: {e}")
