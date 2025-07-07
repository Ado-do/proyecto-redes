import ssl
import socket
import logging
from typing import Tuple

BUFFER_SIZE = 16  # 2+4+4+4+2


class TLSServer:
    def __init__(self, host: str, port: int, certs_path: str):
        self.host = host
        self.port = port
        self.certs_path = certs_path
        self.logger = logging.getLogger("TLSServer")

    def create_ssl_context(self) -> ssl.SSLContext:
        """Setup TLS with mutual auth"""
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(
            certfile=f"{self.certs_path}/server/server.crt",
            keyfile=f"{self.certs_path}/server/server.key",
        )
        ctx.load_verify_locations(cafile=f"{self.certs_path}/ca/ca.crt")
        ctx.verify_mode = ssl.CERT_REQUIRED
        return ctx

    def handle_connection(self, conn: ssl.SSLSocket, addr: Tuple[str, int], data_handler):
        """Process client connection"""
        with conn:
            self.logger.info(f"Connection from {addr[0]}")

            try:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    return

                sensor_data = data_handler.parse_sensor_data(data)
                print(sensor_data)
                if data_handler.validate_data(sensor_data):
                    if data_handler.forward_data(sensor_data):
                        conn.sendall(b"ACK")
                    else:
                        conn.sendall(b"ERR")
                else:
                    conn.sendall(b"ERR")

            except Exception as e:
                self.logger.error(f"Error: {e}")
                conn.sendall(b"ERR")

    def run(self, data_handler):
        """Start the server"""
        context = self.create_ssl_context()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            self.logger.info(f"Server started on {self.host}:{self.port}")

            try:
                while True:
                    conn, addr = sock.accept()
                    try:
                        tls_conn = context.wrap_socket(conn, server_side=True)
                        self.handle_connection(tls_conn, addr, data_handler)
                    except ssl.SSLError as e:
                        self.logger.error(f"TLS error: {e}")
                        conn.close()
            except KeyboardInterrupt:
                self.logger.info("Server stopped")
