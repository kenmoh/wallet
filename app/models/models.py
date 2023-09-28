from datetime import datetime
import uuid
from decimal import Decimal
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DECIMAL, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.schemas.payment_schema import PaymentStatus
from app.utils.utils import unique_id, api_key_gen, api_test_key_gen
from app.database.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, default=unique_id)
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone_number: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str]
    api_key: Mapped[str] = mapped_column(String, default=api_key_gen, unique=True, nullable=True)
    api_test_key: Mapped[str] = mapped_column(String, default=api_test_key_gen, unique=True, nullable=True)
    payment_code: Mapped[str] = mapped_column(nullable=True)
    wallet: Mapped['Wallet'] = relationship('Wallet', uselist=False, back_populates="user",  cascade="all, delete-orphan")
    members: Mapped['GroupMember'] = relationship('GroupMember', uselist=True, back_populates="user",  cascade="all, delete-orphan")
    group: Mapped['Group'] = relationship('Group', uselist=True, back_populates="owner",  cascade="all, delete-orphan")
    withdrawals: Mapped['Withdraw'] = relationship('Withdraw', uselist=False, back_populates="user", cascade="all, delete-orphan")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.username}'


class Wallet(Base):
    __tablename__ = "wallets"
    #
    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    wallet_address: Mapped[uuid] = mapped_column(UUID, default=uuid.uuid1)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    username: Mapped[str]
    user: Mapped[User] = relationship("User", back_populates="wallet")
    payments: Mapped[str] = relationship("Payment", back_populates="wallet")
    transfers: Mapped['Transfer'] = relationship("Transfer", back_populates="wallet")
    withdrawals: Mapped['Withdraw'] = relationship("Withdraw", back_populates="wallet")
    balance: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.wallet_address} -> {self.user}'


class TopUpWallet(Base):
    __tablename__ = 'topups'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    wallet_address: Mapped[uuid.UUID]
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False, default=0.0)
    payment_url: Mapped[str] = mapped_column(String, nullable=True)
    payment_status: Mapped[PaymentStatus] = mapped_column(String, default=PaymentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.wallet_address} -> {self.amount}'


class Transfer(Base):
    __tablename__ = 'transfers'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    wallet_id: Mapped[str] = mapped_column(String, ForeignKey("wallets.id"), nullable=False)
    wallet_address: Mapped[uuid.UUID]
    username: Mapped[str]
    wallet: Mapped[str] = relationship("Wallet", back_populates="transfers")
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.wallet_address} -> {self.amount}'


class Payment(Base):
    __tablename__ = 'payments'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    wallet_id: Mapped[str] = mapped_column(String, ForeignKey("wallets.id"), nullable=False)
    wallet_address: Mapped[uuid.UUID]
    wallet: Mapped[str] = relationship("Wallet", back_populates="payments")
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False, default=0.0)
    merchant: Mapped[str] = mapped_column(default='Kenneth', nullable=True)
    order_id: Mapped[str] = mapped_column(default='', nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f'{self.wallet_address} -> {self.amount}'


class Withdraw(Base):
    __tablename__ = 'withdrawals'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    wallet_id: Mapped[str] = mapped_column(String, ForeignKey("wallets.id"), nullable=False)
    wallet: Mapped[str] = relationship("Wallet", back_populates="withdrawals")
    user: Mapped[str] = relationship("User", back_populates="withdrawals")
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Group(Base):
    __tablename__ = 'groups'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    bill_amount: Mapped[Decimal]
    group_name: Mapped[str]
    members: Mapped[list['GroupMember']] = relationship('GroupMember', back_populates='group')
    owner: Mapped[str] = relationship('User', back_populates='group')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GroupMember(Base):
    __tablename__ = 'group_members'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=unique_id)
    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    group_id: Mapped[str] = mapped_column(String, ForeignKey('groups.id'), nullable=False)
    member_username: Mapped[str]
    amount: Mapped[Decimal] = mapped_column(DECIMAL, nullable=True, default=0.00)
    percentage: Mapped[Decimal] = mapped_column(DECIMAL, nullable=True, default=0.00)
    group: Mapped[str] = relationship('Group', back_populates='members')
    user: Mapped[list[User]] = relationship('User', back_populates='members')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

