"""Точка запуска шлюза Gateway, проксирование на порты 8001/8002."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables
from .api.v1.endpoints import router
from .seed import seed

app = FastAPI(title="mental_stats — main service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_tables()
    seed()


app.include_router(router, prefix="/api/v1")