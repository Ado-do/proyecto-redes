import logging
from tls_server import TLSServer
from data_handler import DataHandler

# Loggin setup
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    # Config
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8080
    CERTS_PATH = "certs"
    FINAL_SERVER_URL = "http://localhost:8000/api/data"

    # Init comps
    data_handler = DataHandler(FINAL_SERVER_URL)
    server = TLSServer(SERVER_HOST, SERVER_PORT, CERTS_PATH)

    # Start server
    server.run(data_handler)


if __name__ == "__main__":
    main()
