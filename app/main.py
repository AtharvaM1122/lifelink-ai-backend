from fastapi import FastAPI

from app.database.connection import engine
from app.database.base import Base

import app.models

from app.routers.users import router as user_router
from app.routers.sos import router as sos_router

app = FastAPI(title="LifeLink AI API")

Base.metadata.create_all(bind=engine)

app.include_router(user_router)
app.include_router(sos_router)


@app.get("/")
def root():
    return {
        "message": "LifeLink AI Backend Running Successfully 🚑"
    }