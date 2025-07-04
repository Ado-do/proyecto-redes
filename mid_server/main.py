import socket
import struct
from datetime import datetime, timezone
import logging

# Logging config
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_sensor_data(data: bytes) -> dict:
    """Parse binary sensor data validation."""
    # Network byte order (big-endian), int16 (2) + 3 floats (12) = 14 bytes
    fmt = "!hfff"
    expected_size = struct.calcsize(fmt)

    logger.debug(f"Received data size: {len(data)} bytes")

    if len(data) != expected_size:
        raise ValueError(f"Invalid data size. Expected {expected_size}, got {len(data)} bytes")

    try:
        unpacked = struct.unpack(fmt, data)
        return {
            "id": unpacked[0],
            # "temperature": unpacked[1],
            # "pressure": unpacked[2],
            # "humidity": unpacked[3],
            "temperature": round(unpacked[1], 2),
            "pressure": round(unpacked[2], 2),
            "humidity": round(unpacked[3], 2),
            "timestamp": datetime.now(timezone.utc).isoformat(), 
        }
    except struct.error as e:
        logger.error(f"Data parsing failed: {e}")
        raise


def verify_data(data: dict) -> bool:
    """Validate sensor readings against physical limits."""
    try:
        return all(
            [
                -50 <= data["temperature"] <= 150,
                300 <= data["pressure"] <= 1200,
                0 <= data["humidity"] <= 100,
            ]
        )
    except KeyError as e:
        logger.error(f"Missing sensor field: {e}")
        return False


def handle_client(conn: socket.socket, addr: tuple):
    """Handle a single client connection."""
    with conn:
        logger.info(f"Connection established from {addr}")

        try:
            # Receive exactly 14 bytes (2 + 4*3)
            data = b""
            while len(data) < 14:
                chunk = conn.recv(14 - len(data))
                if not chunk:
                    logger.warning("Connection closed prematurely")
                    return
                data += chunk

            # Parse and validate
            sensor_data = parse_sensor_data(data)
            logger.info(f"Received valid data: {sensor_data}")

            # Send response
            response = b"ACK" if verify_data(sensor_data) else b"ERR"
            conn.sendall(response)
            logger.debug(f"Sent response: {response.decode()}")

        except (ValueError, struct.error) as e:
            logger.error(f"Data processing error: {e}")
            conn.sendall(b"ERR")
        except socket.error as e:
            logger.error(f"Socket error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            conn.sendall(b"ERR")


def run_server():
    """Run the TCP server indefinitely."""
    # Init TCP socket with IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # For quickly restart server without waiting a previous socket to fully close
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # ip_addr = "0.0.0.0"
        ip_addr = "127.0.0.1"
        port = 8080

        s.bind((ip_addr, port))
        s.listen(5) # backlog of 5
        logger.info(f"Server started on {ip_addr}:{port}")

        try:
            while True:
                conn, addr = s.accept()
                handle_client(conn, addr)
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            logger.info("Server stopped")


if __name__ == "__main__":
    run_server()
