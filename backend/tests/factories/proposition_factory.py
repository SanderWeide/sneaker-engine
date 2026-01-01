"""Proposition model factory for generating test Proposition instances."""
from datetime import datetime, timezone, timedelta
from polyfactory import Use

from models.proposition import Proposition
from .base import BaseFactory


class PropositionFactory(BaseFactory):
    """Factory for generating Proposition model instances.
    
    Usage:
        # Generate a single proposition (not persisted)
        proposition = PropositionFactory.build(seller_id=1, buyer_id=2)
        
        # Generate with specific sneaker
        proposition = PropositionFactory.build(
            seller_id=seller.id, 
            buyer_id=buyer.id,
            sneaker_id=sneaker.id
        )
        
        # Generate multiple propositions
        propositions = PropositionFactory.batch(5, seller_id=1, buyer_id=2)
        
        # Persist to database
        proposition = PropositionFactory.create_sync(
            session=db_session,
            seller_id=seller.id,
            buyer_id=buyer.id
        )
    """
    
    __model__ = Proposition
    
    # Custom field generation
    value = Use(lambda: round(PropositionFactory.__random__.uniform(50.0, 1000.0), 2))
    agreed_datetime = Use(lambda: None)  # Default to None (not agreed yet)
    created_at = Use(lambda: datetime.now(timezone.utc))
    updated_at = Use(lambda: None)
    sneaker_id = Use(lambda: PropositionFactory.__random__.randint(1, 10000))  # Generate random sneaker_id
