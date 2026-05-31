"""Приём алертов от Сервиса 1 и логирование пушей в консоль."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="notification_service", version="0.1.0")


class AlertRequest(BaseModel):
    emp_id: int
    score: int


@app.post("/alert", status_code=202)
def receive_alert(body: AlertRequest):
    print(
        f"[ALERT] Сотрудник #{body.emp_id} набрал {body.score} баллов — требуется беседа.",
        flush=True,
    )
    return {"status": "logged"}


@app.get("/health")
def health():
    return {"status": "ok"}
