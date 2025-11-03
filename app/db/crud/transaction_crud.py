from sqlalchemy.orm import Session
from app.db.models.transaction_model import Transaction
from app.schemas.transaction_schema import TransactionCreate


def create_transaction(db: Session, tx_data: TransactionCreate, user_id: int) -> Transaction:
    """
    Create and store a new transaction record.
    """
    transaction = Transaction(
        user_id=user_id,
        wallet_id=tx_data.wallet_id,
        amount=tx_data.amount,
        transaction_type=tx_data.transaction_type,
        status=tx_data.status,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction_by_id(db: Session, tx_id: int) -> Transaction | None:
    """
    Retrieve transaction details by ID.
    """
    return db.query(Transaction).filter(Transaction.id == tx_id).first()


def list_user_transactions(db: Session, user_id: int, limit: int = 20) -> list[Transaction]:
    """
    Return recent transactions for a given user.
    """
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .all()
    )