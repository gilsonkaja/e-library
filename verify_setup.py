#!/usr/bin/env python
"""
Verification script - Tests that all imports work correctly
Run this to ensure the Flask app will start without errors

Usage:
  python verify_setup.py
"""

import sys
from pathlib import Path

print("\n" + "="*60)
print("Cloud eLibrary - Backend Verification")
print("="*60 + "\n")

# Test Python version
print(f"✓ Python version: {sys.version}")

# Test imports
errors = []
packages = {
    "Flask": "flask",
    "Flask-JWT-Extended": "flask_jwt_extended",
    "bcrypt": "bcrypt",
    "python-dotenv": "dotenv",
    "boto3": "boto3",
    "PyMuPDF": "fitz",
    "pdfminer.six": "pdfminer",
    "requests": "requests",
}

print("\nTesting imports:")
print("-" * 60)

for display_name, import_name in packages.items():
    try:
        __import__(import_name)
        print(f"  ✓ {display_name:<20} OK")
    except ImportError as e:
        print(f"  ✗ {display_name:<20} FAILED: {e}")
        errors.append(f"{display_name}: {e}")

# Test local imports
print("\nTesting local modules:")
print("-" * 60)

try:
    from config import Config
    print(f"  ✓ config.Config              OK")
except Exception as e:
    print(f"  ✗ config.Config              FAILED: {e}")
    errors.append(f"config: {e}")

try:
    from data_store import get_users, save_users, get_books, save_books
    print(f"  ✓ data_store                 OK")
except Exception as e:
    print(f"  ✗ data_store                 FAILED: {e}")
    errors.append(f"data_store: {e}")

try:
    from utils.pdf_extract import extract_text_from_pdf_bytes
    print(f"  ✓ utils.pdf_extract          OK")
except Exception as e:
    print(f"  ✗ utils.pdf_extract          FAILED: {e}")
    errors.append(f"utils.pdf_extract: {e}")

try:
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.upload import upload_bp
    from routes.extract import extract_bp
    from routes.ai import ai_bp
    print(f"  ✓ All route blueprints      OK")
except Exception as e:
    print(f"  ✗ Route blueprints          FAILED: {e}")
    errors.append(f"routes: {e}")

try:
    from app import create_app
    app = create_app()
    print(f"  ✓ Flask app creation         OK")
except Exception as e:
    print(f"  ✗ Flask app creation         FAILED: {e}")
    errors.append(f"app: {e}")

# Test data directory
print("\nTesting data directory:")
print("-" * 60)

data_dir = Path("data")
if data_dir.exists():
    print(f"  ✓ data/ directory exists")
    for json_file in ["users.json", "books.json", "purchases.json"]:
        if (data_dir / json_file).exists():
            print(f"    ✓ {json_file}")
        else:
            print(f"    ✗ {json_file} (missing)")
else:
    print(f"  ✗ data/ directory not found")
    errors.append("data/ directory missing")

# Final summary
print("\n" + "="*60)
if not errors:
    print("✓ ALL CHECKS PASSED - Ready to run Flask app!")
    print("\nStart server with:")
    print("  python app.py")
    print("\nOr use the quick-start script:")
    print("  .\\run.bat")
    print("\nAPI available at: http://localhost:5000/api")
    sys.exit(0)
else:
    print(f"✗ {len(errors)} ERROR(S) FOUND - Please fix before running:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
    print("\nFix: Try running:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

print("="*60 + "\n")
