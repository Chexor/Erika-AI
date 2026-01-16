import sys
import os
import asyncio # New import

# Add root directory to python path
# os.path.dirname(__file__) is 'scripts', so we need dirname of that for root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain import Brain

async def test_brain(): # Changed to async function
    print("🧠 Initializing Brain...")
    brain = Brain()
    
    print("\n🧪 Testing Simple Generation:")
    try:
        response = await brain.think("Hello, are you there?") # Await the coroutine
        print(f"🤖 Response: {response}")
    except Exception as e:
        print(f"❌ Error during generation: {e}")

    print("\n🌊 Testing Stream Generation:")
    try:
        print("🤖 Stream: ", end="", flush=True)
        async for chunk in brain.think_stream("Count to 5"): # Use async for and await
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"❌ Error during streaming: {e}")

if __name__ == "__main__":
    asyncio.run(test_brain()) # Run the async function using asyncio
