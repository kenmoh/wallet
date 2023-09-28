import uuid

from fastapi import APIRouter, status, Depends, Response, HTTPException
from sqlalchemy.orm import Session

from app.schemas.payment_schema import PaymentSchema, PaymentResponseSchema, \
    PaymentCodeSchema
from app.models.models import User
from app.schemas.wallet_schema import WalletResponseSchema
from app.database.database import get_db
from app.services import payment
from app.utils.auth import get_current_user

payment_router = APIRouter(prefix='/api/payments', tags=['Payments'])


@payment_router.get('', status_code=status.HTTP_200_OK)
def get_all_user_payments(user_id: str, db: Session = Depends(get_db)) -> list[PaymentResponseSchema]:
    return payment.user_payments(user_id, db)


@payment_router.post('', status_code=status.HTTP_201_CREATED)
def pay_from_wallet(wallet_address: uuid.UUID, code: PaymentCodeSchema,
                    pay: PaymentSchema, response: Response,
                    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WalletResponseSchema:
    """
    - Pay with wallet
    - This route allow user to pay a merchant with their wallet
    """
    new_payment = payment.pay_with_wallet(wallet_address=wallet_address, code=code, pay=pay, user=current_user, db=db)
    print(response.status_code)
    if not response.status_code == status.HTTP_201_CREATED:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Something went wrong!')
    #publish('success', {"status": "success"})
    return new_payment


@payment_router.get('/{payment_id}', status_code=status.HTTP_200_OK)
def get_payment_details(payment_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> PaymentResponseSchema:
    """
    - Get payment details of a transaction
    """
    return payment.payment_details(payment_id, db, current_user)
