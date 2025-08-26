from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "up"}

@app.get("/hello")
async def hello_world():
    return {"hello": "world"}