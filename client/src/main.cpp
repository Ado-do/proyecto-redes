#include "SensorData.hpp"

#include <arpa/inet.h>
#include <filesystem>
#include <iostream>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <unistd.h>

using namespace std;
namespace fs = std::filesystem;

// Configuration
const fs::path CERTS_PATH = fs::current_path() / "certs";
const string IP = "127.0.0.1";
const int PORT = 8080;

// Host to network SensorData bit order
void hsdtonsd(SensorData &sd) {
    sd.id = htons(sd.id);
    sd.humidity = htonl(sd.humidity);
    sd.pressure = htonl(sd.pressure);
    sd.temperature = htonl(sd.temperature);
    sd.checksum = htons(sd.checksum);
}

SSL_CTX *init_ssl_context() {
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (!ctx) {
        cerr << "SSL context creation failed\n";
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    // Load certificates
    if (!SSL_CTX_load_verify_locations(ctx, (CERTS_PATH / "ca/ca.crt").c_str(), nullptr) ||
        !SSL_CTX_use_certificate_file(ctx, (CERTS_PATH / "client/client.crt").c_str(), SSL_FILETYPE_PEM) ||
        !SSL_CTX_use_PrivateKey_file(ctx, (CERTS_PATH / "client/client.key").c_str(), SSL_FILETYPE_PEM) ||
        !SSL_CTX_check_private_key(ctx)) {
        cerr << "Certificate setup failed\n";
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    return ctx;
}

void cleanup(int sock, SSL_CTX *ctx, SSL *ssl) {
    if (ssl) {
        SSL_shutdown(ssl);
        SSL_free(ssl);
    }
    if (sock != -1)
        close(sock);
    SSL_CTX_free(ctx);
}

int main() {
    // Initialize SSL
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();

    // Verify cert paths
    if (!fs::exists(CERTS_PATH / "ca/ca.crt") || 
        !fs::exists(CERTS_PATH / "client/client.crt") ||
        !fs::exists(CERTS_PATH / "client/client.key")) {
        cerr << "Missing certificate files!\n";
        return EXIT_FAILURE;
    }

    // Init SSL Context
    SSL_CTX *ctx = init_ssl_context();
    int sock = -1;
    SSL *ssl = nullptr;

    try {
        // Create TCP connection
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0)
            throw runtime_error("Socket creation failed");

        sockaddr_in serv_addr = {.sin_family = AF_INET, .sin_port = htons(PORT)};
        inet_pton(AF_INET, IP.c_str(), &serv_addr.sin_addr);

        if (connect(sock, (sockaddr *)&serv_addr, sizeof(serv_addr))) {
            throw runtime_error("Connection failed");
        }

        // Create SSL connection
        ssl = SSL_new(ctx);
        SSL_set_fd(ssl, sock);

        if (SSL_connect(ssl) <= 0) {
            throw runtime_error("SSL handshake failed");
        }
        cout << "Using cipher: " << SSL_get_cipher(ssl) << endl;

        // Verify server certificate
        if (SSL_get_verify_result(ssl) != X509_V_OK) {
            throw runtime_error("Certificate verification failed");
        }

        // Send sensor data
        SensorData data = create_fake_sensor_data();
        data.print_data();
        hsdtonsd(data);

        if (SSL_write(ssl, &data, sizeof(data)) <= 0) {
            throw runtime_error("Data send failed");
        }

        // Get response
        char response[4];
        int bytes = SSL_read(ssl, response, sizeof(response));
        if (bytes > 0) {
            cout << "Server response: " << string(response, bytes) << endl;
        }

    } catch (const exception &e) {
        cerr << "Error: " << e.what() << endl;
        ERR_print_errors_fp(stderr);
        cleanup(sock, ctx, ssl);
        return EXIT_FAILURE;
    }

    cleanup(sock, ctx, ssl);
    return EXIT_SUCCESS;
}
