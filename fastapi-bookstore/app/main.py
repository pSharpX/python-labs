from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.v1.router import api_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def health_check():
    return {"status": "up"}

@app.get("/hello")
async def hello_world():
    return {"hello": "world"}
