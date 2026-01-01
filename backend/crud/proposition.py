from sqlalchemy.orm import Session
from typing import Optional, List
from models.proposition import Proposition
from schemas.proposition import PropositionCreate, PropositionUpdate


def get_proposition(db: Session, proposition_id: int):
    return db.query(Proposition).filter(Proposition.id == proposition_id).first()


def get_propositions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    seller_id: Optional[int] = None,
    buyer_id: Optional[int] = None,
    sneaker_id: Optional[int] = None,
) -> List[Proposition]:
    query = db.query(Proposition)
    
    if seller_id is not None:
        query = query.filter(Proposition.seller_id == seller_id)
    if buyer_id is not None:
        query = query.filter(Proposition.buyer_id == buyer_id)
    if sneaker_id is not None:
        query = query.filter(Proposition.sneaker_id == sneaker_id)
    
    return query.offset(skip).limit(limit).all()


def get_user_propositions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Proposition]:
    """Get all propositions where user is either seller or buyer"""
    query = db.query(Proposition).filter(
        (Proposition.seller_id == user_id) | (Proposition.buyer_id == user_id)
    )
    return query.offset(skip).limit(limit).all()


def create_proposition(db: Session, proposition: PropositionCreate):
    proposition_data = proposition.model_dump()
    
    db_proposition = Proposition(**proposition_data)
    db.add(db_proposition)
    db.commit()
    db.refresh(db_proposition)
    return db_proposition


def update_proposition(db: Session, proposition_id: int, proposition: PropositionUpdate):
    db_proposition = get_proposition(db, proposition_id)
    if not db_proposition:
        return None
    
    update_data = proposition.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_proposition, field, value)
    
    db.commit()
    db.refresh(db_proposition)
    return db_proposition


def delete_proposition(db: Session, proposition_id: int):
    db_proposition = get_proposition(db, proposition_id)
    if not db_proposition:
        return False
    
    db.delete(db_proposition)
    db.commit()
    return True
