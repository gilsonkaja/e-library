from flask import Blueprint, request, jsonify
from data_store import get_books, save_books
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request, get_jwt
from functools import wraps

books_bp = Blueprint("books", __name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if not claims.get("isAdmin"):
            return jsonify({"error":"Admin required"}), 403
        return fn(*args, **kwargs)
    return wrapper

@books_bp.route("/", methods=["GET"])
def list_books():
    return jsonify(get_books())

@books_bp.route("/<id>", methods=["GET"])
def get_book(id):
    books = get_books()
    book = next((b for b in books if b["id"]==id), None)
    if not book: return jsonify({"error":"Book not found"}), 404
    return jsonify(book)

@books_bp.route("/", methods=["POST"])
@jwt_required()
def create_book():
    data = request.get_json() or {}
    title = data.get("title"); author = data.get("author")
    if not title or not author: return jsonify({"error":"title and author required"}), 400
    books = get_books()
    new = {
        "id": str(uuid.uuid4()),
        "title": title,
        "author": author,
        "description": data.get("description",""),
        "filename": data.get("filename"),
        "epubFilename": data.get("epubFilename"),
        "premium": bool(data.get("premium", False)),
        "price": float(data.get("price", 0.0)),
        "categories": data.get("categories", []),
        "uploadedAt": __import__("datetime").datetime.utcnow().isoformat()
    }
    books.append(new); save_books(books)
    return jsonify(new), 201

@books_bp.route("/<id>", methods=["PUT"])
@jwt_required()
def update_book(id):
    books = get_books()
    idx = next((i for i,b in enumerate(books) if b["id"]==id), None)
    if idx is None: return jsonify({"error":"Book not found"}), 404
    data = request.get_json() or {}
    books[idx].update(data)
    save_books(books)
    return jsonify(books[idx])

@books_bp.route("/<id>", methods=["DELETE"])
@admin_required
def delete_book(id):
    books = get_books()
    idx = next((i for i,b in enumerate(books) if b["id"]==id), None)
    if idx is None: return jsonify({"error":"Book not found"}), 404
    deleted = books.pop(idx); save_books(books)
    return jsonify({"success": True, "deleted": deleted})
