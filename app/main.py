
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import private_messages

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

@app.get("/hello")
def hello():
    return {"message": "Hello World"}

app.include_router(private_messages.router)
