"""Sneaker model factory for generating test Sneaker instances."""
from datetime import datetime, timezone
from polyfactory import Use

from models.sneaker import Sneaker
from .base import BaseFactory


class SneakerFactory(BaseFactory):
    """Factory for generating Sneaker model instances.
    
    Usage:
        # Generate a single sneaker (not persisted)
        sneaker = SneakerFactory.build()
        
        # Generate with specific user
        sneaker = SneakerFactory.build(user_id=user.id)
        
        # Generate multiple sneakers
        sneakers = SneakerFactory.batch(10, user_id=user.id)
        
        # Persist to database
        sneaker = SneakerFactory.create_sync(session=db_session, user_id=user.id)
    """
    
    __model__ = Sneaker
    
    # Popular sneaker brands
    BRANDS = ["Nike", "Adidas", "Jordan", "New Balance", "Puma", "Reebok", "Converse", "Vans"]
    
    # Common sneaker sizes (EU sizing)
    SIZES = [38.0, 38.5, 39.0, 39.5, 40.0, 40.5, 41.0, 41.5, 42.0, 42.5, 43.0, 43.5, 44.0, 44.5, 45.0, 45.5, 46.0, 46.5, 47.0]
    
    # Custom field generation
    sku = Use(lambda: f"SKU-{SneakerFactory.__faker__.random_number(digits=8, fix_len=True)}")
    brand = Use(lambda: SneakerFactory.__random__.choice(SneakerFactory.BRANDS))
    model = Use(lambda: f"{SneakerFactory.__faker__.word().title()} {SneakerFactory.__faker__.random_number(digits=3)}")
    size = Use(lambda: SneakerFactory.__random__.choice(SneakerFactory.SIZES))
    color = Use(lambda: SneakerFactory.__faker__.color_name())
    purchase_price = Use(lambda: round(SneakerFactory.__random__.uniform(50.0, 500.0), 2))
    description = Use(lambda: SneakerFactory.__faker__.sentence(nb_words=10) if SneakerFactory.__random__.choice([True, False]) else None)
    created_at = Use(lambda: datetime.now(timezone.utc))
    updated_at = Use(lambda: None)
