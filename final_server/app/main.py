from fastapi import FastAPI
from models import SensorData
from database import DATABASE_PATH
import sqlite3

app = FastAPI()


@app.post("/data")
async def save_data(data: SensorData):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO readings 
        (id, temperature, pressure, humidity, timestamp)
        VALUES (?, ?, ?, ?, ?)""",
        (data.id, data.temperature, data.pressure, data.humidity, data.timestamp),
    )
    conn.commit()
    return {"status": "ok"}
