"""Base factory configuration for Polyfactory test data generation."""
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class BaseFactory(SQLAlchemyFactory):
    """Base factory for all SQLAlchemy model factories.
    
    This provides common configuration for all model factories.
    Individual model factories should inherit from this class.
    """
    
    __is_base_factory__ = True
    __set_relationships__ = False  # Control relationship handling
    __set_foreign_keys__ = True    # Auto-set foreign keys
    __allow_none_optionals__ = False  # Don't generate None for Optional fields
