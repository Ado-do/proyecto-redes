#include "SensorData.hpp"

#include <arpa/inet.h>
#include <filesystem>
#include <iostream>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <unistd.h>

using namespace std;

string certs_path = filesystem::current_path().string() + "/certs/";
const string ip = "127.0.0.1";
const int port = 8080;

// Host float to Network float (convert from host byte order to network byte order)
float htonf(float host_float) {
    uint32_t temp;
    memcpy(&temp, &host_float, sizeof(host_float));
    temp = htonl(temp);
    memcpy(&host_float, &temp, sizeof(host_float));
    return host_float;
}

// Convert Host SensorData to Network SensorData (little to big-endian)
void hsdtonsd(SensorData &sd) {
    sd.id = htons(sd.id);
    sd.humidity = htonf(sd.humidity);
    sd.pressure = htonf(sd.pressure);
    sd.temperature = htonf(sd.temperature);
}

SSL_CTX *create_ssl_context() {
    const SSL_METHOD *method = TLS_client_method();
    SSL_CTX *ctx = SSL_CTX_new(method);
    if (!ctx) {
        perror("Unable to create SSL context");
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }
    return ctx;
}

void configure_context(SSL_CTX *ctx) {
    // Load CA certificate
    if (!SSL_CTX_load_verify_locations(ctx, (certs_path + "ca/ca.crt").c_str(), NULL)) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    // Load client certificate and key
    if (SSL_CTX_use_certificate_file(ctx, (certs_path + "client/client.crt").c_str(), SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    if (SSL_CTX_use_PrivateKey_file(ctx, (certs_path + "client/client.key").c_str(), SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    // Verify private key matches certificate
    if (!SSL_CTX_check_private_key(ctx)) {
        cerr << "Private key does not match the certificate public key\n";
        exit(EXIT_FAILURE);
    }
}

int main() {
    // Init OpenSSL
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();

    // Create SSL context
    SSL_CTX *ctx = create_ssl_context();
    configure_context(ctx);

    // Create TCP socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Socket creation failed");
        return 1;
    }
    sockaddr_in serv_addr = {.sin_family = AF_INET, .sin_port = htons(port)};
    inet_pton(AF_INET, ip.c_str(), &serv_addr.sin_addr);

    // Connect to server using TCP socket
    if (connect(sock, (sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("Failed connection");
        close(sock);
        return 0;
    }

    // Create SSL connection
    SSL *ssl = SSL_new(ctx);
    SSL_set_fd(ssl, sock);

    int ret = SSL_connect(ssl);
    if (ret <= 0) {
        SSL_get_error(ssl, ret);
        ERR_print_errors_fp(stderr);
        SSL_CTX_free(ctx);
        close(sock);
        return 0;
    } else {
        cout << "SSL/TLS connection established\n";
    }

    // Create fake sensor data
    SensorData data = create_fake_sensor_data();
    static_assert(sizeof(SensorData) == 14, "SensorData size mismatch!");
    data.print_data();

    // Convert to network bit order and send
    hsdtonsd(data);
    // int bytes_sent = send(sock, &data, sizeof(data), 0);
    int bytes_sent = SSL_write(ssl, &data, sizeof(data));
    cout << "Bytes sent: " << bytes_sent << endl;

    // Receive server response to data
    char response[4];
    int bytes_received = SSL_read(ssl, response, sizeof(response));
    if (bytes_received < 0) {
        perror("Receive error");
    } else {
        cout << "Server answer: " << string(response, bytes_received) << endl;
    }

    // Cleanup
    SSL_shutdown(ssl);
    SSL_free(ssl);
    close(sock);
    SSL_CTX_free(ctx);

    return 0;
}
