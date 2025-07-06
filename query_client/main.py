import requests
import time
from datetime import datetime


def monitor_sensors():
    while True:
        try:
            # Get latest readings
            response = requests.get(
                "http://localhost:8000/api/readings?limit=1", timeout=2
            )
            data = response.json()

            if data:
                latest = data[0]
                # Temperature alert
                if not (-50 <= latest["temperature"] <= 150):
                    print(
                        f"[{datetime.now()}] ALERT: Temperature {latest['temperature']}°C"
                    )

                # Pressure alert
                if not (300 <= latest["pressure"] <= 1200):
                    print(
                        f"[{datetime.now()}] ALERT: Pressure {latest['pressure']} hPa"
                    )

                # Humidity alert
                if not (0 <= latest["humidity"] <= 100):
                    print(f"[{datetime.now()}] ALERT: Humidity {latest['humidity']}%")

        except requests.exceptions.RequestException as e:
            print(f"Monitoring error: {e}")

        time.sleep(10)  # Check every 10 seconds


if __name__ == "__main__":
    monitor_sensors()
