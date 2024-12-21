import subprocess
import sys
import venv
from pathlib import Path
import os

def check_visual_cpp():
    if sys.platform == "win32":
        # Check for Visual C++ Redistributable
        vcruntime_path = r"C:\Windows\System32\vcruntime140.dll"
        if not os.path.exists(vcruntime_path):
            print("\n❌ Microsoft Visual C++ 14.0 or greater is required.")
            print("Please follow these steps:")
            print("1. Download Visual C++ Build Tools:")
            print("   https://visualstudio.microsoft.com/visual-cpp-build-tools/")
            print("2. Run the installer")
            print("3. Select 'Desktop development with C++'")
            print("4. Install and restart your computer")
            print("5. Run this setup script again")
            return False
    return True

def check_python_version():
    if sys.version_info >= (3, 12):
        print("⚠️  Warning: Python 3.12+ detected. Some packages might not be compatible.")
        print("    Consider using Python 3.11 for better compatibility.")
    elif sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)

def setup_environment():
    try:
        check_python_version()
        
        if not check_visual_cpp():
            sys.exit(1)

        # Get the current directory
        base_path = Path(__file__).parent.absolute()
        venv_path = base_path / ".venv"  # Changed to .venv to match VS Code conventions
        
        # Create virtual environment if it doesn't exist
        if not venv_path.exists():
            print("Creating virtual environment...")
            venv.create(venv_path, with_pip=True, upgrade_deps=True)
        
        # Determine pip path based on platform
        pip_path = venv_path / "Scripts" / "pip.exe" if sys.platform == "win32" else venv_path / "bin" / "pip"
        python_path = venv_path / "Scripts" / "python.exe" if sys.platform == "win32" else venv_path / "bin" / "python"
        
        if not pip_path.exists():
            raise FileNotFoundError(f"Pip not found at {pip_path}")
        
        # Create requirements.txt if it doesn't exist
        requirements_path = base_path / "requirements.txt"
        if not requirements_path.exists():
            with open(requirements_path, "w") as f:
                f.write("# Add your requirements here\n")
        
        # Update pip and setuptools first
        print("Updating pip and setuptools...")
        subprocess.check_call([str(pip_path), "install", "--upgrade", "pip", "setuptools", "wheel"])
        
        # Install requirements
        print("Installing requirements...")
        subprocess.check_call([str(pip_path), "install", "-r", str(requirements_path)])
        
        print("\n✅ Setup complete! Activate your environment with:")
        if sys.platform == "win32":
            print(f"    {venv_path}\\Scripts\\activate")
        else:
            print(f"    source {venv_path}/bin/activate")
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error during package installation: {str(e)}")
        print("Please ensure you have Microsoft Visual C++ Build Tools installed")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    setup_environment()
