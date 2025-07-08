from pydantic import BaseModel


class SensorData(BaseModel):
    id: int
    temperature: float
    pressure: float
    humidity: float
    timestamp: str
