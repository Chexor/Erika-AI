import pytest
from unittest.mock import MagicMock
from interface.controller import Controller

def test_update_window_geometry():
    # Setup
    mock_brain = MagicMock()
    mock_memory = MagicMock()
    controller = Controller(mock_brain, mock_memory)
    
    # Mock settings / persist
    controller.settings = {}
    controller.save_settings = MagicMock()
    
    # Test Data
    new_geometry = {
        'x': 100,
        'y': 200,
        'width': 1280,
        'height': 800
    }
    
    # Action
    controller.update_window_geometry(new_geometry)
    
    # Assert
    assert controller.settings['window_x'] == 100
    assert controller.settings['window_y'] == 200
    assert controller.settings['window_width'] == 1280
    assert controller.settings['window_height'] == 800
    
    # Verify persistence was triggered
    controller.save_settings.assert_called_once()

def test_update_window_geometry_partial():
    # Setup
    mock_brain = MagicMock()
    mock_memory = MagicMock()
    controller = Controller(mock_brain, mock_memory)
    controller.settings = {'window_x': 50, 'window_y': 50}
    controller.save_settings = MagicMock()
    
    # Action - Update only width/height
    controller.update_window_geometry({'width': 1024, 'height': 768})
    
    # Assert - old values remain, new values added
    assert controller.settings['window_x'] == 50
    assert controller.settings['window_y'] == 50
    assert controller.settings['window_width'] == 1024
    assert controller.settings['window_height'] == 768
