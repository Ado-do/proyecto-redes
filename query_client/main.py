import requests
import time
from datetime import datetime

TEMP_MIN = -50
TEMP_MAX = 150

PRESS_MIN = 300
PRESS_MAX = 1200

HUM_MIN = 0
HUM_MAX = 100


def monitor_sensors():
    while True:
        try:
            # Get latest readings
            response = requests.get("http://localhost:8000/api/readings?limit=1", timeout=2)
            data = response.json()

            if data:
                latest = data[0]
                # Temperature alert
                if not (TEMP_MIN <= latest["temperature"] <= TEMP_MAX):
                    print(f"[{datetime.now()}] ALERT: Temperature {latest['temperature']}°C")

                # Pressure alert
                if not (PRESS_MIN <= latest["pressure"] <= PRESS_MAX):
                    print(f"[{datetime.now()}] ALERT: Pressure {latest['pressure']} hPa")

                # Humidity alert
                if not (HUM_MIN <= latest["humidity"] <= HUM_MAX):
                    print(f"[{datetime.now()}] ALERT: Humidity {latest['humidity']}%")

        except requests.exceptions.RequestException as e:
            print(f"Monitoring error: {e}")

        time.sleep(10)  # Check every 10 seconds


if __name__ == "__main__":
    monitor_sensors()
