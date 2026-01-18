
import asyncio
import os
import sys
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.modules.reflector import Reflector
from engine.brain import Brain
from engine.memory import Memory
from engine.network_router import BrainRouter
from engine.logger import setup_engine_logger

async def regenerate():
    print("Initializing...")
    brain = Brain()
    memory = Memory(base_path="chats") 
    router = BrainRouter()
    # FORCE ONLINE for generation
    router.status['remote'] = True
    
    reflector = Reflector(brain, memory, router)
    target_date = datetime.date(2026, 1, 17)
    
    print(f"Regenerating reflection for {target_date}...")
    result = await reflector.reflect_on_day(target_date)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(regenerate())
