#!/usr/bin/env python3
"""
Visioneer Setup Script
Automates the initial setup process
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ is required. Current version:", sys.version)
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed. Please install Node.js 16+ from https://nodejs.org/")
    return False

def create_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python dependencies")

def install_firebase_cli():
    """Install Firebase CLI"""
    return run_command("npm install -g firebase-tools", "Installing Firebase CLI")

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return False
    
    # Generate secret key
    secret_key = secrets.token_hex(32)
    
    # Read template and replace placeholder
    with open(env_example, 'r') as f:
        content = f.read()
    
    content = content.replace('your_secret_key_here', secret_key)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ .env file created with generated secret key")
    print("⚠️  Please edit .env file with your actual API keys and Firebase credentials")
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "app/static/images",
        "app/templates/errors",
        "logs",
        "uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Created necessary directories")
    return True

def main():
    """Main setup function"""
    print("🎬 Welcome to Visioneer Setup!")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_node_version():
        print("⚠️  Node.js is required for Firebase CLI. Continuing without it...")
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing Python dependencies", install_dependencies),
        ("Installing Firebase CLI", install_firebase_cli),
        ("Creating .env file", create_env_file),
        ("Creating directories", create_directories),
    ]
    
    failed_steps = []
    
    for description, step_func in steps:
        if not step_func():
            failed_steps.append(description)
    
    print("\n" + "=" * 50)
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\nPlease resolve these issues and run setup again.")
        sys.exit(1)
    else:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env file with your API keys and Firebase credentials")
        print("2. Set up Firebase project (see SETUP_GUIDE.md)")
        print("3. Run: python run.py")
        print("4. Open: http://localhost:5000")
        print("\nFor detailed setup instructions, see SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
