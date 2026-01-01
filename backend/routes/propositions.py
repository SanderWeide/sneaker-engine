from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import PropositionResponse, PropositionCreate, PropositionUpdate, User as UserSchema
from auth_utils import get_current_user
import crud

router = APIRouter(prefix="/api/propositions", tags=["propositions"])


@router.post("", response_model=PropositionResponse, status_code=201)
def create_proposition(
    proposition: PropositionCreate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Create a new proposition (must be seller or buyer)"""
    # Verify that current user is either seller or buyer (or creating open proposition)
    if proposition.buyer_id is not None:
        if current_user.id not in [proposition.seller_id, proposition.buyer_id]:
            raise HTTPException(
                status_code=403,
                detail="You must be either the seller or buyer to create this proposition"
            )
        
        # Verify seller and buyer are different
        if proposition.seller_id == proposition.buyer_id:
            raise HTTPException(
                status_code=400,
                detail="Seller and buyer must be different users"
            )
    else:
        # For open propositions, only the seller can create it
        if current_user.id != proposition.seller_id:
            raise HTTPException(
                status_code=403,
                detail="You can only create open propositions as the seller"
            )
    
    # Verify sneaker exists
    db_sneaker = crud.get_sneaker(db, proposition.sneaker_id)
    if not db_sneaker:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    
    return crud.create_proposition(db=db, proposition=proposition)


@router.get("", response_model=List[PropositionResponse])
def read_propositions(
    skip: int = 0,
    limit: int = 100,
    seller_id: Optional[int] = None,
    buyer_id: Optional[int] = None,
    sneaker_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get propositions with optional filters"""
    propositions = crud.get_propositions(
        db,
        skip=skip,
        limit=limit,
        seller_id=seller_id,
        buyer_id=buyer_id,
        sneaker_id=sneaker_id
    )
    return propositions


@router.get("/my-propositions", response_model=List[PropositionResponse])
def read_my_propositions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Get all propositions where current user is seller or buyer"""
    propositions = crud.get_user_propositions(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    return propositions


@router.get("/{proposition_id}", response_model=PropositionResponse)
def read_proposition(
    proposition_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Get a specific proposition"""
    db_proposition = crud.get_proposition(db, proposition_id=proposition_id)
    if db_proposition is None:
        raise HTTPException(status_code=404, detail="Proposition not found")
    
    # Verify user has access to this proposition
    # Open propositions (buyer_id is None) are accessible to everyone
    if db_proposition.buyer_id is not None:
        if current_user.id not in [db_proposition.seller_id, db_proposition.buyer_id]:
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this proposition"
            )
    
    return db_proposition


@router.put("/{proposition_id}", response_model=PropositionResponse)
def update_proposition(
    proposition_id: int,
    proposition: PropositionUpdate,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Update a proposition (must be seller)"""
    # TODO check when and by whom a proposition may be updated
    db_proposition = crud.get_proposition(db, proposition_id=proposition_id)
    if db_proposition is None:
        raise HTTPException(status_code=404, detail="Proposition not found")
    
    if db_proposition.agreed_datetime is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot update a proposition that has been agreed"
        )
    
    # Verify user has access to this proposition
    allowed_users = [db_proposition.seller_id]
    if db_proposition.buyer_id is not None:
        allowed_users.append(db_proposition.buyer_id)
    
    if current_user.id not in allowed_users:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this proposition"
        )
    
    updated_proposition = crud.update_proposition(db, proposition_id, proposition)
    return updated_proposition


@router.delete("/{proposition_id}", status_code=204)
def delete_proposition(
    proposition_id: int,
    db: Session = Depends(get_db),
    current_user: UserSchema = Depends(get_current_user)
):
    """Delete a proposition (must be seller or buyer)"""
    # TODO check when and by whom a proposition may be deleted
    db_proposition = crud.get_proposition(db, proposition_id=proposition_id)
    if db_proposition is None:
        raise HTTPException(status_code=404, detail="Proposition not found")
    
    # Verify user has access to this proposition
    allowed_users = [db_proposition.seller_id]
    if db_proposition.buyer_id is not None:
        allowed_users.append(db_proposition.buyer_id)
    
    if current_user.id not in allowed_users:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this proposition"
        )
    
    success = crud.delete_proposition(db, proposition_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete proposition")
