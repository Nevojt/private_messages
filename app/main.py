
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .routers import private_messages
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    docs_url="/docs",
    title="Private Messages API",
    description="API for private messages",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(private_messages.router)
