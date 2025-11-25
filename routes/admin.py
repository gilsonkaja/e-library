from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from data_store import get_users, get_payments, get_purchases, save_users
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

def admin_required():
    """Check if current user is admin"""
    claims = get_jwt()
    if not claims.get("isAdmin"):
        return jsonify({"error": "Admin access required"}), 403
    return None

@admin_bp.route("/customers", methods=["GET"])
@jwt_required()
def get_customers():
    err = admin_required()
    if err: return err
    
    users = get_users()
    purchases = get_purchases()
    payments = get_payments()
    
    # Build customer list with stats
    customers = []
    for user in users:
        if user.get("isAdmin"):
            continue  # Skip admin users
        
        user_purchases = [p for p in purchases if p.get("userId") == user["id"]]
        user_payments = [p for p in payments if p.get("userId") == user["id"]]
        total_spent = sum(p.get("amount", 0) for p in user_payments if p.get("status") == "success")
        
        customers.append({
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "purchaseCount": len(user_purchases),
            "totalSpent": total_spent,
            "joinedAt": user.get("createdAt", "N/A")
        })
    
    return jsonify(customers)

@admin_bp.route("/customer/<customer_id>", methods=["GET"])
@jwt_required()
def get_customer_details(customer_id):
    err = admin_required()
    if err: return err
    
    users = get_users()
    user = next((u for u in users if u["id"] == customer_id), None)
    if not user:
        return jsonify({"error": "Customer not found"}), 404
    
    purchases = get_purchases()
    payments = get_payments()
    
    user_purchases = [p for p in purchases if p.get("userId") == customer_id]
    user_payments = [p for p in payments if p.get("userId") == customer_id]
    
    return jsonify({
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "purchases": user_purchases,
        "payments": user_payments
    })

@admin_bp.route("/customer/<customer_id>", methods=["PUT"])
@jwt_required()
def update_customer(customer_id):
    err = admin_required()
    if err: return err
    
    data = request.get_json() or {}
    users = get_users()
    user = next((u for u in users if u["id"] == customer_id), None)
    if not user:
        return jsonify({"error": "Customer not found"}), 404
    
    # Update allowed fields
    if "name" in data:
        user["name"] = data["name"]
    if "email" in data:
        user["email"] = data["email"]
    
    save_users(users)
    return jsonify({"message": "Customer updated", "customer": user})

@admin_bp.route("/customer/<customer_id>", methods=["DELETE"])
@jwt_required()
def delete_customer(customer_id):
    err = admin_required()
    if err: return err
    
    users = get_users()
    user = next((u for u in users if u["id"] == customer_id), None)
    if not user:
        return jsonify({"error": "Customer not found"}), 404
    
    if user.get("isAdmin"):
        return jsonify({"error": "Cannot delete admin users"}), 400
    
    users = [u for u in users if u["id"] != customer_id]
    save_users(users)
    return jsonify({"message": "Customer deleted"})

@admin_bp.route("/payments", methods=["GET"])
@jwt_required()
def get_all_payments():
    err = admin_required()
    if err: return err
    
    payments = get_payments()
    return jsonify(payments)

@admin_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_analytics():
    err = admin_required()
    if err: return err
    
    users = get_users()
    payments = get_payments()
    purchases = get_purchases()
    
    total_customers = len([u for u in users if not u.get("isAdmin")])
    total_revenue = sum(p.get("amount", 0) for p in payments if p.get("status") == "success")
    total_transactions = len(payments)
    successful_payments = len([p for p in payments if p.get("status") == "success"])
    
    # Payment method breakdown
    card_payments = len([p for p in payments if p.get("method") == "card" and p.get("status") == "success"])
    upi_payments = len([p for p in payments if p.get("method") == "upi" and p.get("status") == "success"])
    
    return jsonify({
        "totalCustomers": total_customers,
        "totalRevenue": total_revenue,
        "totalTransactions": total_transactions,
        "successfulPayments": successful_payments,
        "paymentMethods": {
            "card": card_payments,
            "upi": upi_payments
        }
    })
