import json
from pathlib import Path

BASE = Path(__file__).parent
USERS = BASE / "data" / "users.json"
BOOKS = BASE / "data" / "books.json"
PURCHASES = BASE / "data" / "purchases.json"
PAYMENTS = BASE / "data" / "payments.json"

def ensure():
    BASE.joinpath("data").mkdir(exist_ok=True)
    for f in (USERS, BOOKS, PURCHASES, PAYMENTS):
        if not f.exists():
            f.write_text("[]")

def read(file):
    ensure()
    return json.loads(Path(file).read_text())

def write(file, data):
    ensure()
    Path(file).write_text(json.dumps(data, indent=2))

def get_users(): return read(USERS)
def save_users(u): write(USERS, u)
def get_books(): return read(BOOKS)
def save_books(b): write(BOOKS, b)
def get_purchases(): return read(PURCHASES)
def save_purchases(p): write(PURCHASES, p)
def get_payments(): return read(PAYMENTS)
def save_payments(p): write(PAYMENTS, p)
