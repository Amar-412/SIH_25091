#!/usr/bin/env python3
"""
Local Network Server for NEP-2020 Timetable Generator
This script starts the web app accessible to other devices on your local network.
"""

import socket
import subprocess
import sys
import webbrowser
from web_app import app

def get_local_ip():
    """Get the local IP address of this machine."""
    try:
        # Connect to a remote server to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception:
        return "127.0.0.1"

def main():
    """Start the local network server."""
    local_ip = get_local_ip()
    port = 5000
    
    print("=" * 60)
    print("🚀 NEP-2020 Timetable Generator - Local Network Server")
    print("=" * 60)
    print(f"📱 Local Access:     http://127.0.0.1:{port}")
    print(f"🌐 Network Access:   http://{local_ip}:{port}")
    print("=" * 60)
    print("📋 Instructions:")
    print(f"   • Share this URL with others: http://{local_ip}:{port}")
    print("   • Make sure all devices are on the same WiFi network")
    print("   • Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Open browser automatically
    try:
        webbrowser.open(f"http://{local_ip}:{port}")
        print("🌐 Opening browser...")
    except:
        pass
    
    print("🔄 Starting server...")
    print("=" * 60)
    
    # Start the Flask app
    app.run(
        host='0.0.0.0',  # Listen on all network interfaces
        port=port,
        debug=False,     # Disable debug mode for network access
        threaded=True    # Enable threading for multiple users
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
