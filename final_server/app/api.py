from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .database import get_db, insert_reading
from .models import SensorData
from typing import List
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.post("/data")
async def receive_data(reading: SensorData):
    try:
        insert_reading(reading.model_dump())
        return {"status": "success"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@router.get("/readings", response_model=List[SensorData])
async def get_readings(limit: int = 100):
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return [SensorData(**dict(row)) for row in cursor.fetchall()]


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
