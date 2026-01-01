from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Proposition(Base):
    __tablename__ = "propositions"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sneaker_id = Column(Integer, ForeignKey("sneakers.id"), nullable=False)
    value = Column(Float, nullable=False)
    agreed_datetime = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    seller = relationship("User", foreign_keys=[seller_id], backref="propositions_as_seller")
    buyer = relationship("User", foreign_keys=[buyer_id], backref="propositions_as_buyer")
    sneaker = relationship("Sneaker", backref="propositions")
