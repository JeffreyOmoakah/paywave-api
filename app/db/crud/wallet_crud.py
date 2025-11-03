from sqlalchemy.orm import Session
from app.db.models.wallet_model import Wallet
from app.schemas.wallet_schema import WalletCreate


def create_wallet(db: Session, wallet_data: WalletCreate, user_id: int) -> Wallet:
    """
    Create a wallet for a specific user.
    """
    wallet = Wallet(
        user_id=user_id,
        balance=wallet_data.balance,
        currency=wallet_data.currency,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def get_wallet_by_user(db: Session, user_id: int) -> Wallet | None:
    """
    Retrieve a user's wallet by user_id.
    """
    return db.query(Wallet).filter(Wallet.user_id == user_id).first()


def update_wallet_balance(db: Session, wallet: Wallet, new_balance: float) -> Wallet:
    """
    Update wallet balance after transactions.
    """
    wallet.balance = new_balance
    db.commit()
    db.refresh(wallet)
    return wallet