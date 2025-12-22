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
    with patch('sonosphone.mcp_server.soco.discovery.by_name'):
        server = SonosMCPServer(default_room="Test Room")
        assert server.default_room == "Test Room"
        assert server.current_room == "Test Room"
        assert server.mcp is not None
        assert server.mcp.name == "SonosPhone MCP Server"


@pytest.mark.asyncio
async def test_all_tools_registered():
    """Test that all expected tools are registered."""
    with patch('sonosphone.mcp_server.soco.discovery.by_name'):
        server = SonosMCPServer(default_room="Test Room")
        
        expected_tools = {
            'set_room', 'get_current_room', 'list_available_rooms',
            'play_favorite', 'play_uri', 'set_volume', 'adjust_volume',
            'pause', 'play', 'stop', 'next_track', 'previous_track',
            'toggle_mute', 'list_favorites'
        }
        
        tools_list = await server.mcp.list_tools()
        registered_tools = {tool.name for tool in tools_list}
        
        assert expected_tools == registered_tools


def test_server_has_device_attribute():
    """Test that the server has device attribute."""
    with patch('sonosphone.mcp_server.soco.discovery.by_name'):
        server = SonosMCPServer(default_room="Test Room")
        assert hasattr(server, 'device')
        assert hasattr(server, 'current_room')
        assert hasattr(server, 'default_room')


def test_server_can_be_created_with_custom_name():
    """Test that the server can be created with a custom name."""
    with patch('sonosphone.mcp_server.soco.discovery.by_name'):
        server = SonosMCPServer(name="Custom MCP Server", default_room="Living Room")
        assert server.mcp.name == "Custom MCP Server"
        assert server.default_room == "Living Room"
