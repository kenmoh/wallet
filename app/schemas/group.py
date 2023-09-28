from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field


class CreateGroupSchema(BaseModel):
    bill_amount: Decimal
    group_name: str


class CreateGroupMemberSchema(BaseModel):
    member_username: str
    amount: Decimal | None = Field(default=None)
    percentage: Decimal | None = Field(default=None)


class GroupMemberResponseSchema(CreateGroupMemberSchema):
    user_id: str
    group_id: str
    created_at: datetime


class GroupResponseSchema(CreateGroupSchema):
    id: str
    user_id: str
    created_at: datetime
    members: list[GroupMemberResponseSchema] | None






