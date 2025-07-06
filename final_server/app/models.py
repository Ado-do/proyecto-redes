from pydantic import BaseModel
from datetime import datetime


class SensorReading(BaseModel):
    id: int
    timestamp: str
    temperature: float
    pressure: float
    humidity: float

    @classmethod
    def validate_ranges(cls, data):
        return all(
            [
                -50 <= data["temperature"] <= 150,
                300 <= data["pressure"] <= 1200,
                0 <= data["humidity"] <= 100,
            ]
        )
