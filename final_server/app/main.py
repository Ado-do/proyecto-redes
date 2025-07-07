from fastapi import FastAPI
from pydantic import BaseModel
from database import DATABASE_PATH
import sqlite3

app = FastAPI()


class SensorData(BaseModel):
    id: int
    temperatura: float
    presion: float
    humedad: float
    timestamp: str


@app.post("/data")
async def save_data(data: SensorData):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO sensor_data 
        (id, temperatura, presion, humedad, timestamp)
        VALUES (?, ?, ?, ?, ?)""",
        (data.id, data.temperatura, data.presion, data.humedad, data.timestamp),
    )
    conn.commit()
    return {"status": "ok"}
