import sys
import os

# Add root directory to python path
# os.path.dirname(__file__) is 'scripts', so we need dirname of that for root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.brain import Brain

def test_brain():
    print("🧠 Initializing Brain...")
    brain = Brain()
    
    print("\n🧪 Testing Simple Generation:")
    try:
        response = brain.think("Hello, are you there?")
        print(f"🤖 Response: {response}")
    except Exception as e:
        print(f"❌ Error during generation: {e}")

    print("\n🌊 Testing Stream Generation:")
    try:
        print("🤖 Stream: ", end="", flush=True)
        for chunk in brain.think_stream("Count to 5"):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"❌ Error during streaming: {e}")

if __name__ == "__main__":
    test_brain()
