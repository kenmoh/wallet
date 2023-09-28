FROM python:3-alpine3.16

LABEL maintainer='DigiWallet'

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    adduser \
        --disable-password \
        --no-create-home \
        dw-user

COPY . .

USER dw-user

CMD ["uvicorn", "app.main:app"]
