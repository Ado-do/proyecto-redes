from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path
from .app.database import init_db
from .app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("✅ Database initialized")
    yield


app = FastAPI(lifespan=lifespan)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "app" / "templates"))

# Mount routes
app.include_router(router, prefix="/api")

# Serve static files
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")


@app.get("/")
async def root():
    return {"message": "Sensor Data Server"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(path=str(Path(__file__).parent / "static" / "favicon.ico"))
