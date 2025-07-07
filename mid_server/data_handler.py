import struct
import socket
import requests
import json
from datetime import datetime, timezone
import logging


def compute_checksum(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            lsb = crc & 0x0001
            crc >>= 1
            if lsb:
                crc ^= 0xA001
    return crc


class DataHandler:
    def __init__(self, server_url):
        self.server_url = server_url
        self.logger = logging.getLogger("DataHandler")

    def parse_sensor_data(self, raw_data: bytes) -> dict:
        """Parse binary data into dictionary and verify checksum"""
        try:
            # Unpack binary data (16 bytes: 2+4+4+4+2)
            sensor_id, temp, press, hum, received_checksum = struct.unpack("!hiiiH", raw_data)
            self.logger.debug(
                f"Received SensorData = {{sensor_id = {sensor_id}, temp = {temp}, pressure = {press}, humidity = {hum}, received_checksum = {received_checksum}}}"
            )

            # Verify checksum
            host_order_raw_data = struct.pack("=hiii", sensor_id, temp, press, hum)
            computed_checksum = compute_checksum(host_order_raw_data)
            if computed_checksum != received_checksum:
                self.logger.error(f"Checksum mismatch! Received: {received_checksum}, Computed: {computed_checksum}")
                raise ValueError("Checksum verification failed")
            else:
                self.logger.info("Checksum verification successful")

            return {
                "id": sensor_id,
                "temperature": temp / 100.0,
                "pressure": press / 100.0,
                "humidity": hum / 100.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except struct.error as e:
            self.logger.error(f"Data parsing failed: {e}")
            raise ValueError("Invalid sensor data format")

    def forward_data(self, data: dict) -> bool:
        """Convert data to JSON text and forward to final server"""
        try:
            json_data = json.dumps(data)  # Explicit textual conversion (UTF-8 JSON)
            self.logger.debug(f"Forwarding JSON: {json_data}")

            response = requests.post(
                self.server_url,
                data=json_data,
                timeout=3,
                headers={"Content-Type": "application/json"},
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Forwarding error: {e}")
            return False
