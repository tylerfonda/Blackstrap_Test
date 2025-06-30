#!/usr/bin/env python3
"""
Environment check utility for Blackstrap.
Prints the active database path and OpenAI API key status to help debug
mismatches between CLI and Flask workers.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check and report environment configuration"""
    print("=== Blackstrap Environment Check ===")
    print()
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    
    # Check database path
    db_path = os.environ.get('DATABASE_URL', 'blackstrap.db')
    if db_path.startswith('sqlite:///'):
        db_file = db_path[10:]  # Remove 'sqlite:///' prefix
    else:
        db_file = db_path
    
    full_db_path = os.path.abspath(db_file)
    db_exists = os.path.exists(full_db_path)
    
    print(f"Database path: {full_db_path}")
    print(f"Database exists: {db_exists}")
    if db_exists:
        stat = os.stat(full_db_path)
        print(f"Database size: {stat.st_size} bytes")
    print()
    
    # Check OpenAI API key
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        # Show first 8 and last 4 characters for verification
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"OPENAI_API_KEY: ✓ Set ({masked_key})")
    else:
        print("OPENAI_API_KEY: ✗ Not set")
    print()
    
    # Check if we can import the app
    try:
        sys.path.append(os.getcwd())
        from app import app
        print("Flask app import: ✓ Success")
    except Exception as e:
        print(f"Flask app import: ✗ Failed - {e}")
    print()

if __name__ == "__main__":
    check_environment()

