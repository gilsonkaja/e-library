#!/usr/bin/env python3
"""Simple direct Flask test without HTTP."""

from app import create_app

app = create_app()

# Test the app directly
with app.test_client() as client:
    print("Testing API endpoints...\n")
    
    # Test health
    resp = client.get("/api/health")
    print(f"GET /api/health: {resp.status_code}")
    print(f"  Response: {resp.get_json()}\n")
    
    # Test books
    resp = client.get("/api/books/")
    print(f"GET /api/books/: {resp.status_code}")
    print(f"  Response: {resp.get_json()}\n")
    
    # Test signup
    resp = client.post("/api/auth/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "TestPass123!"
    })
    print(f"POST /api/auth/signup: {resp.status_code}")
    print(f"  Response: {resp.get_json()}\n")
