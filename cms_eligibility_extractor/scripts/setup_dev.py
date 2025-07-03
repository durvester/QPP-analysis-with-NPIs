#!/usr/bin/env python3
"""
Development environment setup script for CMS QPP Eligibility Extractor.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, description="", check=True):
    """Run a command and handle errors."""
    print(f"📋 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   ❌ {e.stderr.strip()}")
        return False


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print(f"   ❌ Python {version.major}.{version.minor} is not supported")
        print("   ℹ️  Please use Python 3.8 or higher")
        return False
    
    print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_git():
    """Check if git is available."""
    print("📦 Checking Git...")
    
    if not shutil.which('git'):
        print("   ❌ Git is not installed")
        return False
    
    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
    print(f"   ✅ {result.stdout.strip()}")
    return True


def setup_virtual_environment():
    """Set up virtual environment if not already in one."""
    print("🏠 Checking virtual environment...")
    
    if sys.prefix == sys.base_prefix:
        print("   ⚠️  Not in a virtual environment")
        print("   ℹ️  Consider creating one:")
        print("      python -m venv venv")
        print("      source venv/bin/activate  # Linux/Mac")
        print("      venv\\Scripts\\activate     # Windows")
        return False
    else:
        print("   ✅ Virtual environment detected")
        return True


def install_dependencies():
    """Install project dependencies."""
    print("📚 Installing dependencies...")
    
    # Upgrade pip first
    if not run_command("python -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install development dependencies
    if not run_command("pip install -e \".[dev,test,docs]\"", "Installing project with dev dependencies"):
        return False
    
    return True


def setup_pre_commit():
    """Set up pre-commit hooks."""
    print("🔧 Setting up pre-commit hooks...")
    
    if not run_command("pre-commit --version", "Checking pre-commit installation"):
        return False
    
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return False
    
    if not run_command("pre-commit install --hook-type commit-msg", "Installing commit message hooks"):
        return False
    
    return True


def create_config_files():
    """Create necessary configuration files."""
    print("⚙️  Creating configuration files...")
    
    # Create .env file from example if it doesn't exist
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("   ✅ Created .env from .env.example")
        print("   ℹ️  Please review and update .env with your settings")
    elif env_file.exists():
        print("   ✅ .env file already exists")
    else:
        print("   ⚠️  No .env.example found to copy from")
    
    # Create necessary directories
    directories = [
        'logs',
        'outputs',
        'temp_uploads', 
        'temp_outputs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created directory: {directory}")
    
    return True


def run_initial_tests():
    """Run initial tests to verify setup."""
    print("🧪 Running initial tests...")
    
    # Check dependencies
    if not run_command("python tests/run_all_tests.py --check-deps", "Checking test dependencies"):
        return False
    
    # Run a quick unit test
    if not run_command("python -m pytest tests/test_api_client_comprehensive.py::TestCMSEligibilityClientInitialization::test_default_initialization -v", 
                      "Running sample test", check=False):
        print("   ⚠️  Test failed - this might be due to missing pytest or other dependencies")
        print("   ℹ️  Try running: pip install pytest")
    
    return True


def validate_configuration():
    """Validate project configuration."""
    print("✅ Validating configuration...")
    
    try:
        # Test configuration loading
        result = subprocess.run([
            'python', '-c', 
            'from src.config import load_config; config = load_config(); config.validate(); print("Configuration valid")'
        ], capture_output=True, text=True, check=True)
        
        print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Configuration validation failed: {e}")
        if e.stderr:
            print(f"   ❌ {e.stderr.strip()}")
        return False


def print_next_steps():
    """Print next steps for the developer."""
    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("   1. Review and update .env file with your configuration")
    print("   2. Run tests: make test")
    print("   3. Start development server: make dev-server")
    print("   4. Run CLI: make dev-cli")
    print("   5. Check code quality: make dev-check")
    print("\n🔧 Useful commands:")
    print("   make help           - Show all available commands")
    print("   make format         - Format code")
    print("   make lint           - Run linting")
    print("   make test-unit      - Run unit tests")
    print("   make test-web       - Run web tests")
    print("   make clean          - Clean build artifacts")
    print("\n📚 Documentation:")
    print("   README.md           - Main project documentation")
    print("   .env.example        - Configuration examples")
    print("   pyproject.toml      - Project configuration")


def main():
    """Main setup function."""
    print("🚀 Setting up CMS QPP Eligibility Extractor development environment")
    print("=" * 70)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_git():
        return 1
    
    # Setup steps
    setup_virtual_environment()  # Warning only, not blocking
    
    if not install_dependencies():
        return 1
    
    if not setup_pre_commit():
        return 1
    
    if not create_config_files():
        return 1
    
    if not validate_configuration():
        print("   ⚠️  Configuration validation failed, but continuing...")
    
    if not run_initial_tests():
        print("   ⚠️  Initial tests had issues, but continuing...")
    
    print_next_steps()
    return 0


if __name__ == '__main__':
    sys.exit(main())