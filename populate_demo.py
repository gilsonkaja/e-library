import requests
import json
import os

BASE_URL = "http://localhost:5000/api"

# Ensure we have a user
def get_token():
    # Try login first
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={"email": "admin@demo.com", "password": "password"})
        if r.status_code == 200:
            return r.json()["token"]
    except:
        pass
    
    # Signup if failed
    try:
        r = requests.post(f"{BASE_URL}/auth/signup", json={"name": "Demo Admin", "email": "admin@demo.com", "password": "password"})
        if r.status_code == 200:
            return r.json()["token"]
    except Exception as e:
        print(f"Auth failed: {e}")
    return None

def create_demo_books(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    books = [
        {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "description": "A novel set in the Jazz Age that tells the story of Jay Gatsby's unrequited love for Daisy Buchanan.",
            "filename": "gatsby.pdf",
            "price": 0.0
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "description": "A dystopian social science fiction novel and cautionary tale about the future.",
            "filename": "1984.pdf",
            "price": 9.99
        },
        {
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "description": "A romantic novel of manners that follows the character development of Elizabeth Bennet.",
            "filename": "pride.pdf",
            "price": 4.99
        },
        {
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "description": "A children's fantasy novel following the quest of home-loving bilbo baggins.",
            "filename": "hobbit.pdf",
            "price": 12.50
        }
    ]
    
    print("Creating demo books...")
    for b in books:
        try:
            r = requests.post(f"{BASE_URL}/books/", json=b, headers=headers)
            if r.status_code == 201:
                print(f"Created: {b['title']}")
            else:
                print(f"Skipped (maybe exists): {b['title']}")
        except Exception as e:
            print(f"Error creating {b['title']}: {e}")

if __name__ == "__main__":
    print("Initializing Demo Data...")
    token = get_token()
    if token:
        create_demo_books(token)
        print("\nSuccess! Refresh the UI to see the books.")
    else:
        print("Could not authenticate. Make sure the server is running.")
