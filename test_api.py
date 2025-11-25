#!/usr/bin/env python3
"""Quick API test script."""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health():
    """Test health endpoint."""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✓ Health check: {resp.status_code}")
        print(f"  Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_books():
    """Test books endpoint."""
    try:
        resp = requests.get(f"{BASE_URL}/books/", timeout=5)
        print(f"✓ Books list: {resp.status_code}")
        print(f"  Response: {resp.json()}")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Books list failed: {e}")
        return False

def test_signup():
    """Test signup."""
    try:
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        resp = requests.post(f"{BASE_URL}/auth/signup", json=payload, timeout=5)
        print(f"✓ Signup: {resp.status_code}")
        print(f"  Response: {resp.json()}")
        return resp.status_code in [201, 200]
    except Exception as e:
        print(f"✗ Signup failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Cloud eLibrary Backend API...\n")
    test_health()
    print()
    test_books()
    print()
    test_signup()
