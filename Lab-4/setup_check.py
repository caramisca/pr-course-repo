"""
Setup Check Script
Verifies that all required dependencies are installed and Docker is running
"""

import sys
import subprocess
import importlib

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  ⚠ Warning: Python 3.8+ recommended")
        return False
    return True


def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        importlib.import_module(package_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Docker is installed: {result.stdout.strip()}")
            
            # Check if Docker daemon is running
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Docker daemon is running")
                return True
            else:
                print("✗ Docker daemon is not running")
                return False
        else:
            print("✗ Docker is NOT installed")
            return False
    except FileNotFoundError:
        print("✗ Docker is NOT installed")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Docker command timed out")
        return False


def check_docker_compose():
    """Check if Docker Compose is installed"""
    try:
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ Docker Compose is installed: {result.stdout.strip()}")
            return True
        else:
            print("✗ Docker Compose is NOT installed")
            return False
    except FileNotFoundError:
        print("✗ Docker Compose is NOT installed")
        return False
    except subprocess.TimeoutExpired:
        print("✗ Docker Compose command timed out")
        return False


def main():
    """Main setup check"""
    print("\n" + "="*80)
    print("SETUP CHECK - Distributed Key-Value Store")
    print("="*80 + "\n")
    
    all_good = True
    
    # Check Python
    print("Checking Python...")
    if not check_python_version():
        all_good = False
    print()
    
    # Check Docker
    print("Checking Docker...")
    if not check_docker():
        all_good = False
    print()
    
    # Check Docker Compose
    print("Checking Docker Compose...")
    if not check_docker_compose():
        all_good = False
    print()
    
    # Check Python packages
    print("Checking Python packages...")
    required_packages = ['flask', 'requests', 'matplotlib', 'numpy']
    for package in required_packages:
        if not check_package(package):
            all_good = False
    print()
    
    # Summary
    print("="*80)
    if all_good:
        print("✓ ALL CHECKS PASSED - You're ready to go!")
        print("="*80)
        print("\nNext steps:")
        print("  1. Start the cluster: docker-compose up -d --build")
        print("  2. Run integration tests: python integration_test.py")
        print("  3. Run performance analysis: python performance_analysis.py")
    else:
        print("✗ SOME CHECKS FAILED - Please install missing dependencies")
        print("="*80)
        print("\nTo install Python packages:")
        print("  pip install -r requirements.txt")
        print("\nTo install Docker:")
        print("  Visit: https://docs.docker.com/get-docker/")
    print()


if __name__ == "__main__":
    main()
