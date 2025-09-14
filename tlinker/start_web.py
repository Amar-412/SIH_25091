#!/usr/bin/env python3
"""
Startup script for the web-based timetable generator.
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['flask', 'pandas', 'ortools', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("Dependencies installed successfully!")

def main():
    """Main function to start the web application."""
    print("🚀 Starting Vicharak - NEP-2020 Timetable Generator Web App...")
    print("=" * 50)
    
    # Check dependencies
    check_dependencies()
    
    # Start the web application
    print("Starting web server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the web app
    from web_app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
