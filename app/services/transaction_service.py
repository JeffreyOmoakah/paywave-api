"""
Transaction Service Layer
--------------------------
Handles all transaction logic:
- Fetching history
- Filtering transactions
- Fraud prevention & audit flags
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.crud import transaction_crud
from datetime import datetime, timedelta


def get_user_transactions(db: Session, user_id: int, limit: int = 20):
    """Fetch recent transactions for a user."""
    return transaction_crud.get_transactions_by_user(db, user_id, limit)


def get_transaction_detail(db: Session, txn_id: int):
    """Fetch single transaction details."""
    txn = transaction_crud.get_transaction_by_id(db, txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


def flag_large_transactions(db: Session, user_id: int, threshold: float = 1000.0):
    """
    Security monitor: Identify large or suspicious transactions.
    Could be used by an admin dashboard or automated alert system.
    """
    txns = transaction_crud.get_transactions_by_user(db, user_id)
    flagged = [txn for txn in txns if txn.amount >= threshold]
    return {"flagged_transactions": flagged}


def detect_unusual_activity(db: Session, user_id: int, minutes: int = 10, count_limit: int = 5):
    """
    Detect unusual frequency of transactions (anti-fraud signal).
    Example: more than 5 transactions in 10 minutes.
    """
    now = datetime.utcnow()
    txns = transaction_crud.get_transactions_by_user(db, user_id)
    recent_txns = [txn for txn in txns if (now - txn.timestamp) < timedelta(minutes=minutes)]

    if len(recent_txns) > count_limit:
        return {"alert": True, "message": "Unusual activity detected", "count": len(recent_txns)}
    return {"alert": False}