"""MCP server for controlling Sonos devices through LLM interfaces."""
import logging
from typing import Optional, List, Dict, Any
import soco
from soco.exceptions import SoCoException
from mcp.server import FastMCP

LOG = logging.getLogger('sonosphone.mcp_server')


class SonosMCPServer:
    """MCP server exposing Sonos control tools for LLM integration."""

    def __init__(self, name: str = "SonosPhone MCP Server"):
        """Initialize the Sonos MCP server.
        
        Args:
            name: Name of the MCP server
        """
        # Initialize FastMCP server
        self.mcp = FastMCP(
            name=name,
            instructions=(
                "This server provides tools to control Sonos speakers. "
                "Each tool accepts a 'room' parameter to specify which Sonos room to control. "
                "You can play music from various services, control volume, and manage playback."
            )
        )
        
        # Register all tools
        self._register_tools()

    def _get_device(self, room_name: str) -> Optional[soco.SoCo]:
        """Helper method to get a Sonos device by room name.
        
        Args:
            room_name: Name of the Sonos room
            
        Returns:
            SoCo device instance or None if not found
        """
        try:
            device = soco.discovery.by_name(room_name)
            return device
        except Exception as e:
            LOG.error(f"Error discovering device '{room_name}': {e}")
            return None

    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.mcp.tool()
        def get_room_status(room: str) -> Dict[str, Any]:
            """Get information about a specific Sonos room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Information about the room and its current playback state
            """
            try:
                device = self._get_device(room)
                
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                track_info = device.get_current_track_info()
                transport_info = device.get_current_transport_info()
                
                return {
                    "success": True,
                    "room": room,
                    "player_name": device.player_name,
                    "is_playing": transport_info.get('current_transport_state') == 'PLAYING',
                    "volume": device.volume,
                    "mute": device.mute,
                    "current_track": track_info.get('title', 'Nothing playing'),
                    "artist": track_info.get('artist', ''),
                    "album": track_info.get('album', '')
                }
            except Exception as e:
                LOG.error(f"Error getting room status for '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def list_available_rooms() -> Dict[str, Any]:
            """List all available Sonos rooms/zones on the network.
            
            Returns:
                List of available room names
            """
            try:
                LOG.info("Discovering Sonos devices")
                zones = soco.discovery.discover()
                
                if zones is None:
                    return {
                        "success": False,
                        "error": "No Sonos devices found on network",
                        "rooms": []
                    }
                
                rooms = [zone.player_name for zone in zones]
                return {
                    "success": True,
                    "rooms": sorted(rooms),
                    "count": len(rooms)
                }
            except Exception as e:
                LOG.error(f"Error discovering rooms: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "rooms": []
                }

        @self.mcp.tool()
        def play_favorite(room: str, favorite_name: str) -> Dict[str, Any]:
            """Play a Sonos favorite by name in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
                favorite_name: Name of the favorite to play
            
            Returns:
                Status of the playback operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Playing favorite '{favorite_name}' in room '{room}'")
                favorites = device.music_library.get_sonos_favorites()
                
                # Find the favorite
                target_favorite = None
                for fav in favorites:
                    if favorite_name.lower() in fav.title.lower():
                        target_favorite = fav
                        break
                
                if target_favorite is None:
                    available = [f.title for f in favorites]
                    return {
                        "success": False,
                        "error": f"Favorite '{favorite_name}' not found",
                        "available_favorites": available,
                        "room": room
                    }
                
                # Clear queue and play
                device.clear_queue()
                device.add_to_queue(target_favorite)
                device.play_from_queue(0)
                
                return {
                    "success": True,
                    "message": f"Playing favorite: {target_favorite.title}",
                    "favorite": target_favorite.title,
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error playing favorite in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def play_uri(room: str, uri: str, title: Optional[str] = None) -> Dict[str, Any]:
            """Play media from a URI in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
                uri: URI of the media to play (e.g., Spotify URI, radio stream URL)
                title: Optional title for the media
            
            Returns:
                Status of the playback operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Playing URI '{uri}' in room '{room}'")
                device.play_uri(uri, title=title or "")
                
                return {
                    "success": True,
                    "message": f"Playing from URI",
                    "uri": uri,
                    "title": title,
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error playing URI in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def set_volume(room: str, volume: int) -> Dict[str, Any]:
            """Set the volume level in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
                volume: Volume level (0-100)
            
            Returns:
                Status of the volume change
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                # Clamp volume to valid range
                volume = max(0, min(100, volume))
                
                LOG.info(f"Setting volume to {volume} in room '{room}'")
                device.volume = volume
                
                return {
                    "success": True,
                    "volume": volume,
                    "message": f"Volume set to {volume}",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error setting volume in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def adjust_volume(room: str, change: int) -> Dict[str, Any]:
            """Adjust the volume by a relative amount in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
                change: Volume change amount (-100 to +100)
            
            Returns:
                Status of the volume change
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Adjusting volume by {change} in room '{room}'")
                current_volume = device.volume
                new_volume = max(0, min(100, current_volume + change))
                device.volume = new_volume
                
                return {
                    "success": True,
                    "previous_volume": current_volume,
                    "new_volume": new_volume,
                    "change": new_volume - current_volume,
                    "message": f"Volume adjusted from {current_volume} to {new_volume}",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error adjusting volume in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def pause(room: str) -> Dict[str, Any]:
            """Pause the current playback in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the pause operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Pausing playback in room '{room}'")
                device.pause()
                
                return {
                    "success": True,
                    "message": "Playback paused",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error pausing in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def play(room: str) -> Dict[str, Any]:
            """Resume or start playback in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the play operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Starting/resuming playback in room '{room}'")
                device.play()
                
                return {
                    "success": True,
                    "message": "Playback started/resumed",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error playing in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def stop(room: str) -> Dict[str, Any]:
            """Stop the current playback in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the stop operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Stopping playback in room '{room}'")
                device.stop()
                
                return {
                    "success": True,
                    "message": "Playback stopped",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error stopping in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def next_track(room: str) -> Dict[str, Any]:
            """Skip to the next track in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the skip operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Skipping to next track in room '{room}'")
                device.next()
                
                # Get the new track info
                track_info = device.get_current_track_info()
                
                return {
                    "success": True,
                    "message": "Skipped to next track",
                    "current_track": track_info.get('title', ''),
                    "artist": track_info.get('artist', ''),
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error skipping to next track in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def previous_track(room: str) -> Dict[str, Any]:
            """Go back to the previous track in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the operation
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Going to previous track in room '{room}'")
                device.previous()
                
                # Get the new track info
                track_info = device.get_current_track_info()
                
                return {
                    "success": True,
                    "message": "Went to previous track",
                    "current_track": track_info.get('title', ''),
                    "artist": track_info.get('artist', ''),
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error going to previous track in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def toggle_mute(room: str) -> Dict[str, Any]:
            """Toggle mute on/off in a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status of the mute toggle
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                current_mute = device.mute
                new_mute = not current_mute
                
                LOG.info(f"Toggling mute in room '{room}': {current_mute} -> {new_mute}")
                device.mute = new_mute
                
                return {
                    "success": True,
                    "mute": new_mute,
                    "message": f"Mute {'on' if new_mute else 'off'}",
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error toggling mute in '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

        @self.mcp.tool()
        def list_favorites(room: str) -> Dict[str, Any]:
            """List all available Sonos favorites from a specific room.
            
            Args:
                room: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                List of favorite names
            """
            try:
                device = self._get_device(room)
                if device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room}' not found",
                        "room": room
                    }
                
                LOG.info(f"Listing favorites from room '{room}'")
                favorites = device.music_library.get_sonos_favorites()
                favorite_list = [{"title": fav.title, "uri": fav.get_uri()} for fav in favorites]
                
                return {
                    "success": True,
                    "favorites": favorite_list,
                    "count": len(favorite_list),
                    "room": room
                }
            except Exception as e:
                LOG.error(f"Error listing favorites from '{room}': {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "room": room
                }

    def run_stdio(self):
        """Run the MCP server with stdio transport."""
        LOG.info("Starting Sonos MCP Server (stdio mode)")
        self.mcp.run()

    async def run_stdio_async(self):
        """Run the MCP server asynchronously with stdio transport."""
        LOG.info("Starting Sonos MCP Server (stdio mode, async)")
        await self.mcp.run_stdio_async()

    def run_http(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the MCP server with HTTP transport.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        LOG.info(f"Starting Sonos MCP Server (HTTP mode) on {host}:{port}")
        self.mcp.run(host=host, port=port)


def main():
    """Main entry point for the MCP server."""
    import sys
    import argparse
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Sonos MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP mode (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on for HTTP mode (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Create and run server (no default room needed)
    server = SonosMCPServer()
    
    if args.transport == "stdio":
        server.run_stdio()
    else:
        server.run_http(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
