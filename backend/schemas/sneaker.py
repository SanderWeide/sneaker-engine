from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SneakerBase(BaseModel):
    sku: str = Field(..., max_length=100)
    brand: str = Field(..., max_length=100)
    model: str = Field(..., max_length=200)
    size: float = Field(..., gt=0)
    color: Optional[str] = Field(None, max_length=100)
    purchase_price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    user_id: int


class SneakerCreate(SneakerBase):
    pass


class SneakerUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=200)
    size: Optional[float] = Field(None, gt=0)
    color: Optional[str] = Field(None, max_length=100)
    purchase_price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    user_id: Optional[int] = None


class Sneaker(SneakerBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
