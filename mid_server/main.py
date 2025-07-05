import os
import ssl
import socket
import struct
from datetime import datetime, timezone
import logging

# Logging config
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
CERTS_PATH = os.path.join("certs", "")  # Ensures trailing slash
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
BUFFER_SIZE = 14
ACK = b"ACK"
ERR = b"ERR"

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
            while len(data) < BUFFER_SIZE:
                chunk = conn.recv(BUFFER_SIZE - len(data))
                if not chunk:
                    logger.warning("Connection closed prematurely")
                    return
                data += chunk

            # Parse and validate
            sensor_data = parse_sensor_data(data)
            logger.info(f"Received valid data: {sensor_data}")

            # Send response
            response = ACK if verify_data(sensor_data) else ERR
            conn.sendall(response)
            logger.debug(f"Sent response: {response.decode()}")

        except (ValueError, struct.error) as e:
            logger.error(f"Data processing error: {e}")
            conn.sendall(ERR)
        except socket.error as e:
            logger.error(f"Socket error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            conn.sendall(ERR)


def run_server():
    """Run the TCP server indefinitely."""

    # Create SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile= CERTS_PATH + "server/server.crt", 
                            keyfile= CERTS_PATH + "server/server.key")
    context.load_verify_locations(cafile=os.path.join(CERTS_PATH, "ca", "ca.crt"))
    context.verify_mode = ssl.CERT_REQUIRED  # Require client certificate

    # Init TCP socket with IPv4
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # For quickly restart server without waiting a previous socket to fully close
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind((SERVER_HOST, SERVER_PORT))
        s.listen(5) # backlog of 5
        logger.info(f"Server started on {SERVER_HOST}:{SERVER_PORT}")

        try:
            while True:
                conn, addr = s.accept()
                try:
                    # Wrap the socket with TLS
                    tls_conn = context.wrap_socket(conn, server_side=True)
                    logger.info(f"TLS connection established with {addr}")
                    handle_client(tls_conn, addr)
                except ssl.SSLError as e:
                    logger.error(f"SSL error: {e}")
                    conn.close()
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    conn.close()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")

if __name__ == "__main__":
    run_server()
