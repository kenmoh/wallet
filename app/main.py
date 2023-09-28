from fastapi import FastAPI, status, Request
from app.models import models
from app.database import database
from app.routers import user_router, topup_router, login, transfer_router, payment_router, group_router
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title='digiWallet', description='Digital wallet for online transactions')


@app.get('/', tags=['Health Check'])
async def health_check():
    return {'health_status': status.HTTP_200_OK}


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    print(data['name'])


@app.post("/items")
async def read_items(request: Request):
    req = request.headers.get("API-KEY")
    return {"API_KEY": req}

app.include_router(login.login_router)
app.include_router(user_router.user_router)
app.include_router(topup_router.top_up_router)
app.include_router(transfer_router.transfer_router)
app.include_router(payment_router.payment_router)
app.include_router(group_router.group_router)
