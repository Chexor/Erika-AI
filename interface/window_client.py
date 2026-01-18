import webview
import argparse
import sys
import os
import time
import threading
import urllib.request
import json

def state_sync_loop(window, api_url):
    """Monitors window state and syncs to engine."""
    last_state = {}
    
    # Wait for window to be ready
    time.sleep(2)
    
    while True:
        try:
            current_state = {
                'x': window.x,
                'y': window.y,
                'width': window.width,
                'height': window.height
            }
            
            # Simple check for changes
            if current_state != last_state:
                # print(f"Client: Window moved/resized: {current_state}")
                try:
                    req = urllib.request.Request(
                        f"{api_url}/api/window/state",
                        data=json.dumps(current_state).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req) as response:
                        pass
                    last_state = current_state
                except Exception as e:
                    # Engine might be down or busy
                    pass
            
            time.sleep(1) # Poll every second
            
        except Exception:
            break

def main():
    parser = argparse.ArgumentParser(description="Erika AI Window Client")
    parser.add_argument("--url", "-u", type=str, required=True, help="URL to load")
    parser.add_argument("--title", "-t", type=str, default="Erika AI", help="Window Title")
    
    # Geometry Args
    parser.add_argument("--x", type=int, default=None, help="Window X Position")
    parser.add_argument("--y", type=int, default=None, help="Window Y Position")
    parser.add_argument("--width", type=int, default=1680, help="Window Width")
    parser.add_argument("--height", type=int, default=1120, help="Window Height")
    
    args = parser.parse_args()
    
    # Path to icon
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'ErikaLogo.ico')
    if not os.path.exists(icon_path):
        icon_path = None # webview will use default

    # Windows Taskbar Icon Fix (AppUserModelID)
    try:
        import ctypes
        appid = 'erika.ai.assistant.v1' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except Exception:
        pass

    # Create Window
    window = webview.create_window(
        args.title, 
        args.url, 
        width=args.width, 
        height=args.height, 
        x=args.x,
        y=args.y,
        resizable=True
    )
    
    
    # Start Sync Thread
    # args.url is like "http://localhost:3333"
    # We want to ensure we don't trip up on trailing slashes
    base_url = args.url.rstrip('/')
        
    t = threading.Thread(target=state_sync_loop, args=(window, base_url), daemon=True)
    t.start()
    
    # Start Loop
    try:
        webview.start(icon=icon_path, debug=False)
    except Exception as e:
        print(f"Window Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
