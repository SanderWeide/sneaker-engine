from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PropositionBase(BaseModel):
    seller_id: int
    buyer_id: Optional[int]
    sneaker_id: int
    value: float = Field(..., gt=0)
    agreed_datetime: Optional[datetime] = None


class PropositionCreate(BaseModel):
    seller_id: int
    buyer_id: Optional[int] = None
    sneaker_id: int
    value: float = Field(..., gt=0)
    agreed_datetime: Optional[datetime] = None


class PropositionUpdate(BaseModel):
    buyer_id: Optional[int] = None
    value: Optional[float] = Field(default=None, gt=0)
    agreed_datetime: Optional[datetime] = None


class PropositionResponse(PropositionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
