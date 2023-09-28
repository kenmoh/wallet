import uuid

from fastapi import APIRouter, status, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.schemas.payment_schema import PaymentStatus
from app.schemas.topup import TopUpSchema, TopUpResponseSchema
from app.models.models import User
from app.schemas.wallet_schema import WalletResponseSchema
from app.database.database import get_db
from app.services import topup_wallet
from app.utils.auth import get_current_user
from app.utils import error_response

top_up_router = APIRouter(prefix='/api/top-up', tags=['Top Up'])
templates = Jinja2Templates(directory="templates")


@top_up_router.get('', status_code=status.HTTP_200_OK)
def get_user_top_ups(user_id: str, db: Session = Depends(get_db)) -> list[TopUpResponseSchema]:
    """
    - Get all top-up by user
    """
    return topup_wallet.user_top_ups(user_id, db)


@top_up_router.post('/{wallet_address}', status_code=status.HTTP_201_CREATED)
def top_up_wallet(wallet_address: uuid.UUID, top_up: TopUpSchema, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WalletResponseSchema:
    """
    - User wallet top-up
    """
    if current_user.wallet.wallet_address == wallet_address:
        return topup_wallet.top_up_db_wallet(wallet_address=wallet_address, top_up=top_up, db=db, user=current_user)


@top_up_router.get('/{top_up_id}', status_code=status.HTTP_200_OK)
def get_top_up_details(top_up_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TopUpResponseSchema:
    """
    - Get the top-up details of a user wallet
    """

    if not current_user:
        error_response.invalid_exception('Unauthorized')
    return topup_wallet.top_up_details(top_up_id, db)


@top_up_router.get(
    "/callback",
    status_code=status.HTTP_200_OK,
    response_description="Payment Successful",
    response_class=HTMLResponse,
)
def top_up_callback(request: Request, db: Session = Depends(get_db)):
    db_payment, payment_status = topup_wallet.payment_callback(request, db)

    if payment_status == "successful":
        db_payment.payment_status = PaymentStatus.SUCCESS
        db.commit()
        return templates.TemplateResponse(
            "successful.html",
            {"request": request},
        )

    elif payment_status == "cancelled":
        db_payment.payment_status = PaymentStatus.CANCELED
        db.commit()
        return templates.TemplateResponse(
            "failed.html",
            {"request": request},
        )

    else:
        db_payment.payment_status = PaymentStatus.FAILED
        db.commit()
        return templates.TemplateResponse(
            "failed.html",
            {"request": request},
        )
