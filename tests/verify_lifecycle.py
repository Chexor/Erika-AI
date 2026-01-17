import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock NiceGUI and other dependencies before importing main
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.app'] = MagicMock()
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()

# Mock Interface/Core
sys.modules['interface.tray'] = MagicMock()
sys.modules['interface.controller'] = MagicMock()

async def verify_lifecycle():
    print("Verifying Lifecycle Hooks...")
    
    # Import hooks from main
    from main import startup, shutdown, active_controllers
    import interface.tray
    
    # Setup Mocks
    mock_tray_class = interface.tray.ErikaTray
    mock_tray_instance = mock_tray_class.return_value
    
    mock_controller = MagicMock()
    active_controllers.append(mock_controller)
    
    # Test Startup
    print("[1] Testing Startup...")
    await startup()
    
    # Verify Tray Initialized and Run
    mock_tray_class.assert_called_once()
    mock_tray_instance.run.assert_called_once()
    print("    -> Tray initialized and run: OK")
    
    # Test Shutdown
    print("[2] Testing Shutdown...")
    await shutdown()
    
    # Verify Tray Stopped
    mock_tray_instance.stop.assert_called_once()
    print("    -> Tray stopped: OK")
    
    # Verify Controller Cleanup
    mock_controller.cleanup.assert_called_once()
    print("    -> Controller cleanup called: OK")
    
    print("\nLifecycle Verification Passed!")

if __name__ == "__main__":
    asyncio.run(verify_lifecycle())
