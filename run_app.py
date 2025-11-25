#!/usr/bin/env python
"""
Simple Flask app launcher script
Run: python run_app.py
"""

import sys
import os

# Add current directory to path to import local modules
sys.path.insert(0, os.path.dirname(__file__))

# Import and run Flask app
from app import create_app

if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5000)
    print(f"\n{'='*60}")
    print("Cloud eLibrary - Flask Backend")
    print(f"{'='*60}")
    print(f"\n✓ Server starting on http://localhost:{port}")
    print(f"✓ Press Ctrl+C to stop\n")
    
    try:
        app.run(host="0.0.0.0", port=port, debug=True)
    except KeyboardInterrupt:
        print("\n✓ Server stopped.")
        sys.exit(0)
