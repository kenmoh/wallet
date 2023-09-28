from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, UUID1, Field


class PaymentSchema(BaseModel):
    amount: Decimal


class PaymentStatus(str, Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    CANCELED = 'canceled'
    FAILED = 'failed'


class PaymentCodeSchema(BaseModel):
    payment_code: str = Field(max_length=6, min_length=4)


class PaymentResponseSchema(PaymentSchema):
    id: str
    user_id: str
    wallet_id: UUID1
    wallet_address: UUID1
    merchant: str | None
    created_at: datetime


