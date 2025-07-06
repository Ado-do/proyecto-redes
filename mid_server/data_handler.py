import struct
import requests
from datetime import datetime, timezone
import logging


class DataHandler:
    def __init__(self, server_url):
        self.server_url = server_url
        self.logger = logging.getLogger("DataHandler")

    def parse_sensor_data(self, raw_data: bytes) -> dict:
        """Parse binary data into dictionary"""
        try:
            sensor_id, temp, pressure, humidity = struct.unpack("!hfff", raw_data)
            return {
                "id": sensor_id,
                "temperature": round(temp, 2),
                "pressure": round(pressure, 2),
                "humidity": round(humidity, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except struct.error as e:
            self.logger.error(f"Data parsing failed: {e}")
            raise ValueError("Invalid sensor data format")

    def validate_data(self, data: dict) -> bool:
        """Check physical limits"""
        try:
            return all(
                [
                    -50 <= data["temperature"] <= 150,
                    300 <= data["pressure"] <= 1200,
                    0 <= data["humidity"] <= 100,
                ]
            )
        except KeyError as e:
            self.logger.error(f"Missing sensor field: {e}")
            return False

    def forward_data(self, data: dict) -> bool:
        """Send data to final server with detailed error handling"""
        try:
            self.logger.debug(f"Attempting to forward data: {data}")

            response = requests.post(
                self.server_url,
                json=data,
                timeout=3,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                self.logger.info(
                    f"Successfully forwarded data from sensor {data['id']}"
                )
                return True
            else:
                self.logger.error(
                    f"Forwarding failed with status {response.status_code}. "
                    f"Response: {response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during forwarding: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected forwarding error: {str(e)}")
            return False
