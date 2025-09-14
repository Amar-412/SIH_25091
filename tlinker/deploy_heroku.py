#!/usr/bin/env python3
"""
Deployment script for Heroku hosting.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    """Main deployment function."""
    print("Deploying Vicharak - NEP-2020 Timetable Generator to Heroku")
    print("=" * 60)
    
    # Check if Heroku CLI is installed
    print("🔍 Checking Heroku CLI...")
    heroku_check = run_command("heroku --version", "Checking Heroku CLI")
    if not heroku_check:
        print("❌ Heroku CLI not found!")
        print("Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Get app name from user
    app_name = input("Enter your Heroku app name (or press Enter for auto-generated): ").strip()
    if not app_name:
        app_name = "timetable-generator-" + str(hash(os.getcwd()) % 10000)
    
    print(f"📱 App name: {app_name}")
    
    # Initialize git if not already done
    if not os.path.exists('.git'):
        run_command("git init", "Initializing Git repository")
    
    # Add all files
    run_command("git add .", "Adding files to Git")
    
    # Commit changes
    run_command('git commit -m "Deploy timetable generator"', "Committing changes")
    
    # Create Heroku app
    print(f"🌐 Creating Heroku app: {app_name}")
    create_result = run_command(f"heroku create {app_name}", "Creating Heroku app")
    
    if not create_result:
        print("❌ Failed to create Heroku app. It might already exist.")
        print("Try a different app name or delete the existing app.")
        return
    
    # Deploy to Heroku
    print("🚀 Deploying to Heroku...")
    deploy_result = run_command("git push heroku main", "Deploying to Heroku")
    
    if deploy_result:
        print("🎉 Deployment successful!")
        print(f"🌐 Your app is available at: https://{app_name}.herokuapp.com")
        print("🔗 Opening in browser...")
        run_command(f"heroku open", "Opening app in browser")
    else:
        print("❌ Deployment failed. Check the error messages above.")
        print("💡 Common solutions:")
        print("   - Make sure you're logged in: heroku login")
        print("   - Check your app name is unique")
        print("   - Verify all files are committed")

if __name__ == "__main__":
    main()
