from fastapi import FastAPI
from contextlib import asynccontextmanager
from .app.database import init_db
from .app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize on startup
    init_db()
    print("✅ Database initialized")
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Sensor Data Server"}
