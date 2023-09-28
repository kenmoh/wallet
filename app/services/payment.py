import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


from app.models.models import Wallet, Payment, User
from app.schemas.payment_schema import PaymentSchema, PaymentCodeSchema
from app.database.database import session
from app.utils import error_response
from app.utils.utils import hash_payment_code, verify_payment_code


def create_payment_code(code: PaymentCodeSchema, db: Session):
    """
    This helper function create a code 4-digit code for making payments
    """
    try:
        payment_code = User(payment_code=hash_payment_code(code.payment_code))
        db.commit()
        db.refresh(payment_code)
        return payment_code

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


def pay_with_wallet(wallet_address: uuid.UUID, pay: PaymentSchema,
                    user: User, db: session, code: PaymentCodeSchema):
    """
    - A helper function that allow user to pay with wallet on checkout
    """
    # payment_code = db.query(User).filter(User.payment_code ==
    #                                      code.payment_code).first()
    pay_to_wallet = db.query(Wallet).filter(Wallet.wallet_address == wallet_address).first()
    pay_from_wallet = db.query(Wallet).filter(Wallet.wallet_address == user.wallet.wallet_address).first()

    if pay_from_wallet.balance == 0 or pay_from_wallet.balance < pay.amount:
        error_response.invalid_exception('Insufficient fund. Top up wallet!')

    try:
        new_payment = Payment(
            amount=pay.amount,
            user_id=user.id,
            wallet_id=user.wallet.id,
            wallet_address=pay_to_wallet.wallet_address,
            merchant=pay_to_wallet.username,
            created_at=datetime.today()
        )

        if not verify_payment_code(code.payment_code, user.payment_code):
            error_response.invalid_exception('Invalid payment password!')

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        pay_to_wallet.balance += new_payment.amount
        pay_from_wallet.balance -= new_payment.amount

        db.commit()
        db.refresh(pay_to_wallet)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return pay_from_wallet


def user_payments(user_id: str, db: Session):
    """
    - This helper function get user payment history from the database
    """
    return db.query(Payment).filter(Payment.user_id == user_id).all()


def payment_details(payment_id: str, db: Session, user: User):
    """
    - This helper function get payment details from the database
    """
    return db.query(Payment).filter(Payment.id == payment_id).filter(Payment.user_id == user.id).first()


# def pay_order_with_wallet(wallet_address: uuid.UUID, pay: PaymentSchema, user: User, db: session):
#     """
#     - A helper function that allow user to pay with wallet
#     """
#     pay_to_wallet = db.query(Wallet).filter(Wallet.wallet_address == wallet_address).first()
#     pay_from_wallet = db.query(Wallet).filter(Wallet.wallet_address == user.wallet.wallet_address).first()
#
#     if pay_from_wallet.balance == 0 or pay_from_wallet.balance < pay.amount:
#         error_response.invalid_exception('Insufficient fund. Top up wallet!')
#
#     try:
#         new_payment = Payment(
#             amount=pay.amount,
#             user_id=user.id,
#             wallet_id=user.wallet.id,
#             wallet_address=pay_to_wallet.wallet_address,
#             merchant=pay_to_wallet.username,
#             created_at=datetime.today()
#         )
#
#         db.add(new_payment)
#         db.commit()
#         db.refresh(new_payment)
#
#         pay_to_wallet.balance += new_payment.amount
#         pay_from_wallet.balance -= new_payment.amount
#
#         db.commit()
#         db.refresh(pay_to_wallet)
#
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
#
#     return pay_from_wallet
