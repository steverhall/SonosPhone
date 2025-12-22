"""MCP server for controlling Sonos devices through LLM interfaces."""
import logging
from typing import Optional, List, Dict, Any
import soco
from soco.exceptions import SoCoException
from mcp.server import FastMCP

LOG = logging.getLogger('sonosphone.mcp_server')


class SonosMCPServer:
    """MCP server exposing Sonos control tools for LLM integration."""

    def __init__(self, name: str = "SonosPhone MCP Server", default_room: str = "Kitchen"):
        """Initialize the Sonos MCP server.
        
        Args:
            name: Name of the MCP server
            default_room: Default Sonos room/zone to control
        """
        self.default_room = default_room
        self.current_room = default_room
        self.device: Optional[soco.SoCo] = None
        
        # Initialize FastMCP server
        self.mcp = FastMCP(
            name=name,
            instructions=(
                "This server provides tools to control Sonos speakers. "
                "You can set rooms, play music from various services, "
                "control volume, and manage playback."
            )
        )
        
        # Register all tools
        self._register_tools()

    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.mcp.tool()
        def set_room(room_name: str) -> Dict[str, Any]:
            """Set the active Sonos room/zone to control.
            
            Args:
                room_name: Name of the Sonos room (e.g., "Kitchen", "Living Room")
            
            Returns:
                Status information about the room selection
            """
            try:
                LOG.info(f"Setting room to: {room_name}")
                self.current_room = room_name
                self.device = soco.discovery.by_name(room_name)
                
                if self.device is None:
                    return {
                        "success": False,
                        "error": f"Room '{room_name}' not found",
                        "current_room": None
                    }
                
                return {
                    "success": True,
                    "current_room": room_name,
                    "player_name": self.device.player_name,
                    "household_id": self.device.household_id
                }
            except Exception as e:
                LOG.error(f"Error setting room: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "current_room": self.current_room
                }

        @self.mcp.tool()
        def get_current_room() -> Dict[str, Any]:
            """Get information about the currently selected room.
            
            Returns:
                Information about the current room and its state
            """
            try:
                if self.device is None:
                    # Try to discover the current room
                    self.device = soco.discovery.by_name(self.current_room)
                
                if self.device is None:
                    return {
                        "success": False,
                        "error": "No device connected",
                        "current_room": self.current_room
                    }
                
                track_info = self.device.get_current_track_info()
                transport_info = self.device.get_current_transport_info()
                
                return {
                    "success": True,
                    "current_room": self.current_room,
                    "player_name": self.device.player_name,
                    "is_playing": transport_info.get('current_transport_state') == 'PLAYING',
                    "volume": self.device.volume,
                    "mute": self.device.mute,
                    "current_track": track_info.get('title', 'Nothing playing'),
                    "artist": track_info.get('artist', ''),
                    "album": track_info.get('album', '')
                }
            except Exception as e:
                LOG.error(f"Error getting current room info: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "current_room": self.current_room
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
        def play_favorite(favorite_name: str) -> Dict[str, Any]:
            """Play a Sonos favorite by name.
            
            Args:
                favorite_name: Name of the favorite to play
            
            Returns:
                Status of the playback operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info(f"Playing favorite: {favorite_name}")
                favorites = self.device.music_library.get_sonos_favorites()
                
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
                        "available_favorites": available
                    }
                
                # Clear queue and play
                self.device.clear_queue()
                self.device.add_to_queue(target_favorite)
                self.device.play_from_queue(0)
                
                return {
                    "success": True,
                    "message": f"Playing favorite: {target_favorite.title}",
                    "favorite": target_favorite.title
                }
            except Exception as e:
                LOG.error(f"Error playing favorite: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def play_uri(uri: str, title: Optional[str] = None) -> Dict[str, Any]:
            """Play media from a URI.
            
            Args:
                uri: URI of the media to play (e.g., Spotify URI, radio stream URL)
                title: Optional title for the media
            
            Returns:
                Status of the playback operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info(f"Playing URI: {uri}")
                self.device.play_uri(uri, title=title or "")
                
                return {
                    "success": True,
                    "message": f"Playing from URI",
                    "uri": uri,
                    "title": title
                }
            except Exception as e:
                LOG.error(f"Error playing URI: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def set_volume(volume: int) -> Dict[str, Any]:
            """Set the volume level.
            
            Args:
                volume: Volume level (0-100)
            
            Returns:
                Status of the volume change
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                # Clamp volume to valid range
                volume = max(0, min(100, volume))
                
                LOG.info(f"Setting volume to: {volume}")
                self.device.volume = volume
                
                return {
                    "success": True,
                    "volume": volume,
                    "message": f"Volume set to {volume}"
                }
            except Exception as e:
                LOG.error(f"Error setting volume: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def adjust_volume(change: int) -> Dict[str, Any]:
            """Adjust the volume by a relative amount.
            
            Args:
                change: Volume change amount (-100 to +100)
            
            Returns:
                Status of the volume change
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info(f"Adjusting volume by: {change}")
                current_volume = self.device.volume
                new_volume = max(0, min(100, current_volume + change))
                self.device.volume = new_volume
                
                return {
                    "success": True,
                    "previous_volume": current_volume,
                    "new_volume": new_volume,
                    "change": new_volume - current_volume,
                    "message": f"Volume adjusted from {current_volume} to {new_volume}"
                }
            except Exception as e:
                LOG.error(f"Error adjusting volume: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def pause() -> Dict[str, Any]:
            """Pause the current playback.
            
            Returns:
                Status of the pause operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Pausing playback")
                self.device.pause()
                
                return {
                    "success": True,
                    "message": "Playback paused"
                }
            except Exception as e:
                LOG.error(f"Error pausing: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def play() -> Dict[str, Any]:
            """Resume or start playback.
            
            Returns:
                Status of the play operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Starting/resuming playback")
                self.device.play()
                
                return {
                    "success": True,
                    "message": "Playback started/resumed"
                }
            except Exception as e:
                LOG.error(f"Error playing: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def stop() -> Dict[str, Any]:
            """Stop the current playback.
            
            Returns:
                Status of the stop operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Stopping playback")
                self.device.stop()
                
                return {
                    "success": True,
                    "message": "Playback stopped"
                }
            except Exception as e:
                LOG.error(f"Error stopping: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def next_track() -> Dict[str, Any]:
            """Skip to the next track.
            
            Returns:
                Status of the skip operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Skipping to next track")
                self.device.next()
                
                # Get the new track info
                track_info = self.device.get_current_track_info()
                
                return {
                    "success": True,
                    "message": "Skipped to next track",
                    "current_track": track_info.get('title', ''),
                    "artist": track_info.get('artist', '')
                }
            except Exception as e:
                LOG.error(f"Error skipping to next track: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def previous_track() -> Dict[str, Any]:
            """Go back to the previous track.
            
            Returns:
                Status of the operation
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Going to previous track")
                self.device.previous()
                
                # Get the new track info
                track_info = self.device.get_current_track_info()
                
                return {
                    "success": True,
                    "message": "Went to previous track",
                    "current_track": track_info.get('title', ''),
                    "artist": track_info.get('artist', '')
                }
            except Exception as e:
                LOG.error(f"Error going to previous track: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def toggle_mute() -> Dict[str, Any]:
            """Toggle mute on/off.
            
            Returns:
                Status of the mute toggle
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                current_mute = self.device.mute
                new_mute = not current_mute
                
                LOG.info(f"Toggling mute: {current_mute} -> {new_mute}")
                self.device.mute = new_mute
                
                return {
                    "success": True,
                    "mute": new_mute,
                    "message": f"Mute {'on' if new_mute else 'off'}"
                }
            except Exception as e:
                LOG.error(f"Error toggling mute: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

        @self.mcp.tool()
        def list_favorites() -> Dict[str, Any]:
            """List all available Sonos favorites.
            
            Returns:
                List of favorite names
            """
            try:
                if self.device is None:
                    self.device = soco.discovery.by_name(self.current_room)
                    if self.device is None:
                        return {
                            "success": False,
                            "error": f"Room '{self.current_room}' not found"
                        }
                
                LOG.info("Listing favorites")
                favorites = self.device.music_library.get_sonos_favorites()
                favorite_list = [{"title": fav.title, "uri": fav.get_uri()} for fav in favorites]
                
                return {
                    "success": True,
                    "favorites": favorite_list,
                    "count": len(favorite_list)
                }
            except Exception as e:
                LOG.error(f"Error listing favorites: {e}")
                return {
                    "success": False,
                    "error": str(e)
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
        "--room",
        default="Kitchen",
        help="Default Sonos room to control (default: Kitchen)"
    )
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
    
    # Create and run server
    server = SonosMCPServer(default_room=args.room)
    
    if args.transport == "stdio":
        server.run_stdio()
    else:
        server.run_http(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
