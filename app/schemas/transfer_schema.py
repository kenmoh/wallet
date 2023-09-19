import decimal
import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class TransferSchema(BaseModel):
    amount: decimal.Decimal = Field(ge=500)


class TransferResponseSchema(BaseModel):
    id: str
    user_id: str
    amount: decimal.Decimal
    wallet_id: uuid.UUID
    wallet_address: uuid.UUID
    created_at: datetime
    username: str
