import webview
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Erika AI Window Client")
    parser.add_argument("--url", "-u", type=str, required=True, help="URL to load")
    parser.add_argument("--title", "-t", type=str, default="Erika AI", help="Window Title")
    args = parser.parse_args()
    
    # Path to icon
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'icon.png')
    if not os.path.exists(icon_path):
        icon_path = None # webview will use default

    # Create Window
    # confirm_close=False -> Just close. Process dies. Engine lives safely.
    webview.create_window(args.title, args.url, width=1680, height=1120, resizable=True)
    
    # Start Loop
    # gui='mshtml' or 'edgechromium' or 'cef'. Standard is fine.
    try:
        webview.start(icon=icon_path, debug=False)
    except Exception as e:
        print(f"Window Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
