from fastapi import FastAPI
from routes import router
from db import init_db

app=FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"message":"Server is up and running"}

@app.on_event("startup")
async def on_startup():
    await init_db()