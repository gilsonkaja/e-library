from flask import Blueprint, request, jsonify, current_app
from data_store import get_users, save_users
import bcrypt, uuid
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = data.get("name"); email = data.get("email"); password = data.get("password")
    if not name or not email or not password:
        return jsonify({"error":"name, email and password required"}), 400

    users = get_users()
    if any(u for u in users if u["email"].lower()==email.lower()):
        return jsonify({"error":"Email already in use"}), 400

    is_admin = len(users)==0
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = {"id": str(uuid.uuid4()), "name": name, "email": email, "passwordHash": pw_hash, "isAdmin": is_admin}
    users.append(user); save_users(users)
    # Use the user id as the JWT identity (string) and place extra info in additional_claims
    token = create_access_token(identity=user["id"], additional_claims={"email": user["email"], "isAdmin": is_admin})
    safe = {"id": user["id"], "name": user["name"], "email": user["email"], "isAdmin": is_admin}
    return jsonify({"token": token, "user": safe})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email"); password = data.get("password")
    if not email or not password:
        return jsonify({"error":"email and password required"}), 400
    users = get_users()
    user = next((u for u in users if u["email"].lower()==email.lower()), None)
    if not user:
        return jsonify({"error":"Invalid credentials"}), 400
    if not bcrypt.checkpw(password.encode(), user["passwordHash"].encode()):
        return jsonify({"error":"Invalid credentials"}), 400
    token = create_access_token(identity=user["id"], additional_claims={"email": user["email"], "isAdmin": user["isAdmin"]})
    safe = {"id": user["id"], "name": user["name"], "email": user["email"], "isAdmin": user["isAdmin"]}
    return jsonify({"token": token, "user": safe})
