from PIL import Image
import os

def convert():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    src = os.path.join(base_dir, 'assets', 'ErikaLogo_v3.png')
    dst = os.path.join(base_dir, 'assets', 'ErikaLogo.ico')
    
    if not os.path.exists(src):
        print(f"Source not found: {src}")
        return

    try:
        img = Image.open(src)
        # Resize/Resample for high quality ICO
        # ICO usually contains multiple sizes: 16, 32, 48, 64, 128, 256
        img.save(dst, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print(f"Successfully created: {dst}")
    except Exception as e:
        print(f"Error converting: {e}")

if __name__ == "__main__":
    convert()
