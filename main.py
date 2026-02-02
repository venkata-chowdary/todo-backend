from fastapi import FastAPI
from app.routes import router
from app.auth.routes import router as auth_router
from app.db import init_db
from dotenv import load_dotenv
load_dotenv() 

app=FastAPI()
app.include_router(router)
app.include_router(auth_router)


@app.get("/")
def read_root():
    return {"message":"Server is up and running"}

@app.on_event("startup")
async def on_startup():
    await init_db()
    
    
from redis.asyncio import Redis
# @app.on_event("startup")
# async def startup_event():
#     app.state.redis = Redis(host="localhost", port=6379)


# @app.on_event("shutdown")
# async def shutdown_event():
#     app.state.redis.close()