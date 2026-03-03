from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api import tasks



Base.metadata.create_all(bind=engine)
app=FastAPI(title="Task Management API",description="B2B Task Management App",version="1.0.0")


app.add_middleware(
    CORSMiddleware,allow_origins=[settings.FRONTEND_URL],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])



app.include_router(tasks.router)
