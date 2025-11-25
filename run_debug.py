#!/usr/bin/env python3
"""Run Flask with error logging."""

import logging
import sys
import os

# Set UTF-8 encoding for output
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

try:
    from app import create_app
    print("[OK] App imported")
    
    app = create_app()
    print("[OK] App created")
    print(f"[OK] Config PORT: {app.config['PORT']}")
    
    print("\n[OK] Starting Flask server...\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    
except Exception as e:
    print(f"\n[ERROR] FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
