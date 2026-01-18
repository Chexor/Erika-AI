
import asyncio
import os
import sys
import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from domain.subconscious.reflection_service import ReflectionService
from domain.subconscious.growth_service import GrowthService
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
    
    reflection_service = ReflectionService(brain, memory, router)
    growth_service = GrowthService(brain, router)
    
    target_date = datetime.date(2026, 1, 17)
    
    print(f"Regenerating reflection for {target_date}...")
    status, content = await reflection_service.reflect_on_day(target_date)
    print(f"Result: {status}")
    
    if status == "Completed" and content:
        print("Triggering Evolution...")
        await growth_service.evolve(content)
        print("Done.")

if __name__ == "__main__":
    asyncio.run(regenerate())
