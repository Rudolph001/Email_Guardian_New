# Email Guardian - Manual Installation Helper
# Use this if the main setup script fails

import subprocess
import sys

def install_basic_packages():
    """Install packages one by one with error handling"""
    
    # Essential packages only
    essential_packages = [
        "Flask",
        "Flask-SQLAlchemy", 
        "pandas",
        "numpy",
        "scikit-learn",
        "networkx",
        "email-validator",
        "waitress"
    ]
    
    print("Installing essential packages for Email Guardian...")
    print("This is a simplified installation for compatibility.")
    
    failed_packages = []
    
    for package in essential_packages:
        try:
            print(f"\nInstalling {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--user"
            ])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n⚠️  Failed to install: {', '.join(failed_packages)}")
        print("Try installing these manually:")
        for package in failed_packages:
            print(f"  pip install {package}")
    else:
        print("\n🎉 All essential packages installed successfully!")
        print("You can now run: python local_app.py")

if __name__ == "__main__":
    install_basic_packages()