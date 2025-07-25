# FastAPI entry
from fastapi import FastAPI
from backend.routes.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
