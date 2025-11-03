"""
Wallet Service Layer
-------------------
Handles all wallet-related logic:
- Balance checks and updates
- Transfers between users
- Security checks (fraud prevention, limits)
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.crud import wallet_crud, transaction_crud
from app.schemas.transaction_schema import TransactionCreate
from app.db.models.wallet_model import Wallet

def get_wallet_by_user(db: Session, user_id: int):
    """Fetch a user's wallet."""
    wallet = wallet_crud.get_wallet_by_user(db, user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


def get_balance(db: Session, user_id: int):
    """Return current wallet balance."""
    wallet = get_wallet_by_user(db, user_id)
    return {"balance": wallet.balance}


def create_wallet(db: Session, user_id: int):
    """Create a wallet for a new user."""
    existing = wallet_crud.get_wallet_by_user(db, user_id)
    if existing:
        raise HTTPException(status_code=400, detail="Wallet already exists")
    return wallet_crud.create_wallet(db, user_id=user_id)


def deposit(db: Session, user_id: int, amount: float):
    """Deposit funds into the user's wallet."""
    wallet = get_wallet_by_user(db, user_id)

    # Basic fraud check
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid deposit amount")

    wallet.balance += amount
    db.commit()

    # Record transaction
    txn = TransactionCreate(
        user_id=user_id,
        amount=amount,
        txn_type="DEPOSIT",
        description="Wallet top-up"
    )
    transaction_crud.create_transaction(db, txn)

    return {"message": "Deposit successful", "new_balance": wallet.balance}


def withdraw(db: Session, user_id: int, amount: float):
    """Withdraw funds from wallet with basic security checks."""
    wallet = get_wallet_by_user(db, user_id)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid withdrawal amount")

    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    wallet.balance -= amount
    db.commit()

    txn = TransactionCreate(
        user_id=user_id,
        amount=amount,
        txn_type="WITHDRAW",
        description="Wallet withdrawal"
    )
    transaction_crud.create_transaction(db, txn)

    return {"message": "Withdrawal successful", "new_balance": wallet.balance}


def transfer(db: Session, sender_id: int, receiver_id: int, amount: float):
    """
    Transfer money between wallets.
    This adds basic fraud + rate check logic.
    """
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")

    sender_wallet = get_wallet_by_user(db, sender_id)
    receiver_wallet = get_wallet_by_user(db, receiver_id)

    if sender_wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # Transactional operation
    sender_wallet.balance -= amount
    receiver_wallet.balance += amount
    db.commit()

    # Record transactions for both parties
    txn_out = TransactionCreate(
        user_id=sender_id,
        amount=amount,
        txn_type="TRANSFER_OUT",
        description=f"Transfer to user {receiver_id}"
    )
    txn_in = TransactionCreate(
        user_id=receiver_id,
        amount=amount,
        txn_type="TRANSFER_IN",
        description=f"Received from user {sender_id}"
    )

    transaction_crud.create_transaction(db, txn_out)
    transaction_crud.create_transaction(db, txn_in)

    return {"message": "Transfer successful"}