from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from data_store import get_payments, save_payments, get_books
import uuid
from datetime import datetime

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/initiate", methods=["POST"])
@jwt_required()
def initiate_payment():
    """Initiate a payment for a book"""
    data = request.get_json() or {}
    book_id = data.get("bookId")
    method = data.get("method")  # "card" or "upi"
    
    if not book_id or not method:
        return jsonify({"error": "bookId and method required"}), 400
    
    if method not in ["card", "upi"]:
        return jsonify({"error": "Invalid payment method"}), 400
    
    # Get book details
    books = get_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    user_id = get_jwt_identity()
    
    # Create payment record
    payment = {
        "id": str(uuid.uuid4()),
        "userId": user_id,
        "bookId": book_id,
        "amount": book.get("price", 0),
        "method": method,
        "status": "pending",
        "createdAt": datetime.utcnow().isoformat(),
        "transactionId": None
    }
    
    payments = get_payments()
    payments.append(payment)
    save_payments(payments)
    
    # In demo mode, return payment ID for frontend to "process"
    return jsonify({
        "paymentId": payment["id"],
        "amount": payment["amount"],
        "method": method,
        "status": "pending"
    })

@payment_bp.route("/verify", methods=["POST"])
@jwt_required()
def verify_payment():
    """Verify and complete a payment (demo mode - auto success)"""
    data = request.get_json() or {}
    payment_id = data.get("paymentId")
    transaction_id = data.get("transactionId", str(uuid.uuid4()))
    
    if not payment_id:
        return jsonify({"error": "paymentId required"}), 400
    
    payments = get_payments()
    payment = next((p for p in payments if p["id"] == payment_id), None)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    user_id = get_jwt_identity()
    if payment["userId"] != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    # Demo mode: Auto-approve payment
    payment["status"] = "success"
    payment["transactionId"] = transaction_id
    payment["completedAt"] = datetime.utcnow().isoformat()
    
    save_payments(payments)
    
    return jsonify({
        "status": "success",
        "payment": payment
    })

@payment_bp.route("/history", methods=["GET"])
@jwt_required()
def get_payment_history():
    """Get current user's payment history"""
    user_id = get_jwt_identity()
    payments = get_payments()
    
    user_payments = [p for p in payments if p.get("userId") == user_id]
    return jsonify(user_payments)
