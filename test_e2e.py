#!/usr/bin/env python3
import io
import json
from app import create_app

app = create_app()

with app.test_client() as client:
    print("Starting E2E test...\n")
    # Signup (first user becomes admin)
    signup_payload = {"name": "e2eadmin", "email": "e2e@example.com", "password": "StrongPass123"}
    r = client.post('/api/auth/signup', json=signup_payload)
    print('SIGNUP', r.status_code, r.get_json())
    if r.status_code in (200,201):
        token = r.get_json().get('token')
    else:
        # If user already exists, try logging in
        print('Signup failed, trying login...')
        login_payload = {"email": signup_payload["email"], "password": signup_payload["password"]}
        r2 = client.post('/api/auth/login', json=login_payload)
        print('LOGIN', r2.status_code, r2.get_json())
        if r2.status_code != 200:
            raise SystemExit('Signup and login failed')
        token = r2.get_json().get('token')
    headers = {"Authorization": f"Bearer {token}"}

    # Create a book with no file yet
    book_payload = {"title":"E2E Book","author":"Test Author","description":"E2E test"}
    r = client.post('/api/books/', json=book_payload, headers=headers)
    print('CREATE BOOK', r.status_code, r.get_json())
    if r.status_code != 201 and r.status_code != 200:
        raise SystemExit('Create book failed')
    book = r.get_json()

    # Upload a sample text file (not a real PDF) to exercise upload
    sample_bytes = b"This is a sample document. It contains some text for extraction testing."
    data = {
        'file': (io.BytesIO(sample_bytes), 'sample.txt')
    }
    r = client.post('/api/upload/', data=data, content_type='multipart/form-data')
    print('UPLOAD', r.status_code, r.get_json())
    if r.status_code != 200:
        raise SystemExit('Upload failed')
    upload_info = r.get_json()

    # Attach filename to book by updating it
    update = {'filename': upload_info['filename']}
    r = client.put(f"/api/books/{book['id']}", json=update, headers=headers)
    print('UPDATE BOOK', r.status_code, r.get_json())

    # Attempt to summarize via AI endpoint
    r = client.post('/api/ai/summarize', json={"bookId": book['id']}, headers=headers)
    print('SUMMARIZE', r.status_code, r.get_json())
    
    print('\nE2E test complete')
