from fastapi import APIRouter, HTTPException
from .database import get_db, insert_reading
from .models import SensorReading

router = APIRouter()


@router.post("/data")
async def receive_data(reading: SensorReading):
    try:
        if not SensorReading.validate_ranges(reading.model_dump()):
            raise HTTPException(status_code=400, detail="Invalid sensor ranges")

        insert_reading(reading.model_dump())
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/readings")
async def get_readings(limit: int = 100):
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM readings ORDER BY timestamp DESC LIMIT ?", (limit,)
        )
        return cursor.fetchall()
