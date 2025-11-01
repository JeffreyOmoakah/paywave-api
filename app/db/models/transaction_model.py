from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)  # deposit, withdraw, transfer
    amount = Column(Numeric(12, 2), nullable=False)
    reference = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    wallet = relationship("Wallet", back_populates="transactions")