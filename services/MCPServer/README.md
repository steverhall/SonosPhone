# Sonos MCP Server - systemd Service

This directory contains the systemd service configuration for running the Sonos MCP Server as a Linux service.

## Overview

The Sonos MCP Server provides a Model Context Protocol interface for LLM-based control of Sonos speakers. When run as a service, it operates in HTTP mode, allowing remote clients to connect and control Sonos devices on the network.

## Installation

### 1. Prerequisites

```bash
# Install Python dependencies
pip install -r /path/to/SonosPhone/requirements.txt

# Create service user (optional but recommended for security)
sudo useradd -r -s /bin/false sonosphone

# Create log directory
sudo mkdir -p /var/log/sonosphone
sudo chown sonosphone:sonosphone /var/log/sonosphone
```

### 2. Install Service Files

```bash
# Create installation directory
sudo mkdir -p /opt/services/MCPServer

# Copy the entire sonosphone package
sudo cp -r /path/to/SonosPhone/sonosphone /opt/services/MCPServer/

# Copy the service runner
sudo cp /path/to/SonosPhone/services/MCPServer/run_mcp_server.py /opt/services/MCPServer/

# Set permissions
sudo chown -R sonosphone:sonosphone /opt/services/MCPServer

# Copy systemd service file
sudo cp /path/to/SonosPhone/services/MCPServer/SonosMCPServer.service /etc/systemd/system/

# Create environment configuration directory
sudo mkdir -p /etc/sonosphone

# Copy and customize environment file
sudo cp /path/to/SonosPhone/services/MCPServer/mcp_server.env.example /etc/sonosphone/mcp_server.env
sudo chown root:root /etc/sonosphone/mcp_server.env
sudo chmod 644 /etc/sonosphone/mcp_server.env
```

### 3. Configure the Service

Edit the environment file to customize settings:

```bash
sudo nano /etc/sonosphone/mcp_server.env
```

Available configuration options:
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `MCP_HOST`: Network interface to bind to (default: 0.0.0.0)
- `MCP_PORT`: Port to listen on (default: 8000)
- `MCP_TRANSPORT`: Transport mode (default: http)

### 4. Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable sonosphone-mcp.service

# Start the service
sudo systemctl start sonosphone-mcp.service

# Check service status
sudo systemctl status sonosphone-mcp.service
```

## Service Management

### Check Service Status

```bash
sudo systemctl status sonosphone-mcp.service
```

### View Logs

```bash
# View recent logs
sudo journalctl -u sonosphone-mcp.service -n 50

# Follow logs in real-time
sudo journalctl -u sonosphone-mcp.service -f

# View logs since last boot
sudo journalctl -u sonosphone-mcp.service -b
```

### Restart Service

```bash
sudo systemctl restart sonosphone-mcp.service
```

### Stop Service

```bash
sudo systemctl stop sonosphone-mcp.service
```

### Disable Service

```bash
sudo systemctl disable sonosphone-mcp.service
```

## Testing the Service

Once the service is running, you can test it using curl:

```bash
# Test HTTP endpoint (adjust port if you changed it)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Troubleshooting

### Service won't start

1. Check the service status for error messages:
   ```bash
   sudo systemctl status sonosphone-mcp.service
   ```

2. Verify Python dependencies are installed:
   ```bash
   python3 -c "from sonosphone.mcp_server import SonosMCPServer; print('OK')"
   ```

3. Check permissions:
   ```bash
   ls -la /opt/services/MCPServer
   ls -la /var/log/sonosphone
   ```

### Can't discover Sonos devices

1. Ensure the service user has network access
2. Check that Sonos devices are on the same network
3. Verify multicast is not blocked by firewall:
   ```bash
   sudo ufw allow 1900/udp  # SSDP discovery
   ```

### Port already in use

If port 8000 is already in use, either:
1. Change the port in `/etc/sonosphone/mcp_server.env`
2. Update the port in `/etc/systemd/system/SonosMCPServer.service`
3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart sonosphone-mcp.service
   ```

## Security Considerations

The service file includes several security hardening measures:

- **NoNewPrivileges**: Prevents privilege escalation
- **PrivateTmp**: Isolated temporary directory
- **ProtectSystem**: Read-only access to system directories
- **ProtectHome**: No access to user home directories
- **Dedicated user**: Runs as unprivileged `sonosphone` user

For production deployments, consider:

1. **Firewall rules**: Only allow access from trusted networks
   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8000
   ```

2. **Reverse proxy**: Use nginx or apache as a reverse proxy with HTTPS
3. **Authentication**: The current implementation has no built-in auth
4. **Network isolation**: Run on an isolated management network

## Integration with Claude Desktop

While the service runs in HTTP mode, you can still use it with Claude Desktop by configuring a local client that connects to the HTTP endpoint. However, for Claude Desktop, the stdio mode (run directly, not as a service) is typically preferred.

For remote access or integration with other LLM platforms, the HTTP service mode is ideal.

## Uninstallation

```bash
# Stop and disable the service
sudo systemctl stop sonosphone-mcp.service
sudo systemctl disable sonosphone-mcp.service

# Remove service files
sudo rm /etc/systemd/system/SonosMCPServer.service
sudo rm -rf /opt/services/MCPServer
sudo rm -rf /etc/sonosphone

# Remove logs (optional)
sudo rm -rf /var/log/sonosphone

# Remove service user (optional)
sudo userdel sonosphone

# Reload systemd
sudo systemctl daemon-reload
```

## Additional Notes

- The service runs in HTTP mode by default, listening on all interfaces (0.0.0.0)
- For stdio mode (e.g., with Claude Desktop), run the script directly rather than as a service
- The service automatically restarts on failure with a 10-second delay
- Logs are sent to systemd journal for centralized logging

## Support

For issues or questions, refer to the main SonosPhone repository documentation.
