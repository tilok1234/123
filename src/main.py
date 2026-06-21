import sys
import os

# Add project root to sys.path so 'src' imports work consistently
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app import run_app

if __name__ == "__main__":
    run_app()
