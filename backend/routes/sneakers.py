from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import Sneaker as SneakerSchema, SneakerCreate, SneakerUpdate
import crud

router = APIRouter(prefix="/api/sneakers", tags=["sneakers"])


@router.post("", response_model=SneakerSchema, status_code=201)
def create_sneaker(sneaker: SneakerCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = crud.get_user(db, user_id=sneaker.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.create_sneaker(db=db, sneaker=sneaker)


@router.get("", response_model=List[SneakerSchema])
def read_sneakers(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    sku: Optional[str] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    sneakers = crud.get_sneakers(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        sku=sku,
        brand=brand,
        model=model
    )
    return sneakers


@router.get("/{sneaker_id}", response_model=SneakerSchema)
def read_sneaker(sneaker_id: int, db: Session = Depends(get_db)):
    db_sneaker = crud.get_sneaker(db, sneaker_id=sneaker_id)
    if db_sneaker is None:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    return db_sneaker


@router.put("/{sneaker_id}", response_model=SneakerSchema)
def update_sneaker(sneaker_id: int, sneaker: SneakerUpdate, db: Session = Depends(get_db)):
    db_sneaker = crud.update_sneaker(db, sneaker_id=sneaker_id, sneaker=sneaker)
    if db_sneaker is None:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    return db_sneaker


@router.delete("/{sneaker_id}")
def delete_sneaker(sneaker_id: int, db: Session = Depends(get_db)):
    success = crud.delete_sneaker(db, sneaker_id=sneaker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sneaker not found")
    return {"message": "Sneaker deleted successfully"}
