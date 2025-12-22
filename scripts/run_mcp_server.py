#!/usr/bin/env python3
"""Start the Sonos MCP Server."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sonosphone.mcp_server import main

if __name__ == "__main__":
    main()
