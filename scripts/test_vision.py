
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.brain import Brain

def test_vision():
    brain = Brain()
    # Test with one of our asset images
    image_path = os.path.abspath('assets/Erika-AI_logo.png')
    
    print(f"Testing Vision with: {image_path}")
    if not os.path.exists(image_path):
        print("Error: Test image not found.")
        return

    description = brain.analyze_image(image_path)
    print("\n--- Image Description ---")
    print(description)
    print("-------------------------\n")

if __name__ == "__main__":
    test_vision()
