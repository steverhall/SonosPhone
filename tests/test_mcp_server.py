"""Tests for the Sonos MCP Server."""
import pytest
from unittest.mock import Mock, patch
from sonosphone.mcp_server import SonosMCPServer


@pytest.fixture
def mock_device():
    """Create a mock Sonos device."""
    device = Mock()
    device.player_name = "Test Room"
    device.household_id = "test-household-id"
    device.volume = 50
    device.mute = False
    device.get_current_track_info.return_value = {
        'title': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album'
    }
    device.get_current_transport_info.return_value = {
        'current_transport_state': 'PLAYING'
    }
    return device


def test_server_initialization():
    """Test that the server initializes correctly."""
    server = SonosMCPServer()
    assert server.mcp is not None
    assert server.mcp.name == "SonosPhone MCP Server"


@pytest.mark.asyncio
async def test_all_tools_registered():
    """Test that all expected tools are registered."""
    server = SonosMCPServer()
    
    expected_tools = {
        'get_room_status', 'list_available_rooms',
        'play_favorite', 'play_uri', 'set_volume', 'adjust_volume',
        'pause', 'play', 'stop', 'next_track', 'previous_track',
        'toggle_mute', 'list_favorites'
    }
    
    tools_list = await server.mcp.list_tools()
    registered_tools = {tool.name for tool in tools_list}
    
    assert expected_tools == registered_tools


def test_server_can_be_created_with_custom_name():
    """Test that the server can be created with a custom name."""
    server = SonosMCPServer(name="Custom MCP Server")
    assert server.mcp.name == "Custom MCP Server"


def test_get_device_helper():
    """Test the _get_device helper method."""
    with patch('sonosphone.mcp_server.soco.discovery.by_name') as mock_discovery:
        mock_device = Mock()
        mock_device.player_name = "Test Room"
        mock_discovery.return_value = mock_device
        
        server = SonosMCPServer()
        device = server._get_device("Test Room")
        
        assert device is not None
        assert device.player_name == "Test Room"
        mock_discovery.assert_called_once_with("Test Room")
