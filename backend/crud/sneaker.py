from sqlalchemy.orm import Session
from typing import Optional
from models.sneaker import Sneaker
from schemas.sneaker import SneakerCreate, SneakerUpdate


def get_sneaker(db: Session, sneaker_id: int):
    return db.query(Sneaker).filter(Sneaker.id == sneaker_id).first()


def get_sneakers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    sku: Optional[str] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
):
    query = db.query(Sneaker)
    
    if user_id is not None:
        query = query.filter(Sneaker.user_id == user_id)
    if sku is not None:
        query = query.filter(Sneaker.sku == sku)
    if brand is not None:
        query = query.filter(Sneaker.brand.ilike(f"%{brand}%"))
    if model is not None:
        query = query.filter(Sneaker.model.ilike(f"%{model}%"))
    
    return query.offset(skip).limit(limit).all()


def create_sneaker(db: Session, sneaker: SneakerCreate):
    db_sneaker = Sneaker(**sneaker.model_dump())
    db.add(db_sneaker)
    db.commit()
    db.refresh(db_sneaker)
    return db_sneaker


def update_sneaker(db: Session, sneaker_id: int, sneaker: SneakerUpdate):
    db_sneaker = get_sneaker(db, sneaker_id)
    if not db_sneaker:
        return None
    
    update_data = sneaker.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sneaker, field, value)
    
    db.commit()
    db.refresh(db_sneaker)
    return db_sneaker


def delete_sneaker(db: Session, sneaker_id: int):
    db_sneaker = get_sneaker(db, sneaker_id)
    if db_sneaker:
        db.delete(db_sneaker)
        db.commit()
        return True
    return False
