from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    balance = Column(Numeric(12, 2), default=0)
    currency = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationships
    owner = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet", cascade="all, delete-orphan")