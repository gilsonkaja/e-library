#!/usr/bin/env python3
"""Test Flask app import."""

import sys
import traceback

try:
    from app import create_app
    print("✓ App imported successfully")
    
    app = create_app()
    print("✓ App created successfully")
    
    with app.app_context():
        print("✓ App context created")
        print(f"✓ Registered blueprints: {list(app.blueprints.keys())}")
        
except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()
    sys.exit(1)
