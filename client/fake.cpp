#include <arpa/inet.h>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <random>
#include <unistd.h>

using namespace std;

const string ip = "127.0.0.1";
const int port = 8080;

struct SensorData {
    int16_t id;
    float temperature;
    float pressure;
    float humidity;
} __attribute__((packed)); // Disable padding (14 bytes)

void print_sensor_data(SensorData &sd) {
    cout << fixed << setprecision(2) << "SensorData: {"
         << "'id': " << sd.id << ", "
         << "'temperature': " << sd.temperature << ", "
         << "'pressure': " << sd.pressure << ", "
         << "'humidity': " << sd.humidity << "}"
         << endl;
}

// Setup TCP Socket
void setup_tcp_socket(int *sock, sockaddr_in *sock_addr) {
    *sock = socket(AF_INET, SOCK_STREAM, 0);
    sock_addr->sin_family = AF_INET;
    sock_addr->sin_port = htons(port);
    inet_pton(AF_INET, ip.c_str(), &sock_addr->sin_addr);
}

// Create random fake sensor data
SensorData create_fake_sensor_data() {
    static int16_t id = 0;
    static random_device rd;
    static mt19937 gen(rd());

    uniform_real_distribution<float> temp_distr(-50, 150);
    uniform_real_distribution<float> press_distr(300, 1200);
    uniform_real_distribution<float> hum_distr(0, 100);

    SensorData sd{id++, temp_distr(gen), press_distr(gen), hum_distr(gen)};
    return sd;
}

// Host float to Network float (convert from host byte order to network byte order)
float htonf(float host_float) {
    uint32_t temp;
    memcpy(&temp, &host_float, sizeof(host_float));
    temp = htonl(temp);
    memcpy(&host_float, &temp, sizeof(host_float));
    return host_float;
}

// Convert Host SensorData to Network SensorData (little to big-endian)
SensorData hsdtonsd(SensorData sd) {
    sd.id = htons(sd.id);
    sd.humidity = htonf(sd.humidity);
    sd.pressure = htonf(sd.pressure);
    sd.temperature = htonf(sd.temperature);
    return sd;
}

int main() {
    // Create TCP socket
    int socket;
    sockaddr_in serv_addr;
    setup_tcp_socket(&socket, &serv_addr);

    // Connect to server using TCP socket
    if (connect(socket, (sockaddr *)&serv_addr, sizeof(serv_addr)) == -1) {
        perror("Failed connection");
        return 0;
    }

    // Create fake sensor data
    SensorData data = create_fake_sensor_data();
    static_assert(sizeof(SensorData) == 14, "SensorData size mismatch!");
    print_sensor_data(data);

    // Convert to network bit order and send
    data = hsdtonsd(data);
    int bytes_sent = send(socket, &data, sizeof(data), 0);
    cout << "Bytes sent: " << bytes_sent << endl;

    // Receive server response to data
    char response[4];
    int bytes_received = recv(socket, response, sizeof(response), 0);
    if (bytes_received < 0) {
        perror("Receive error");
    } else {
        cout << "Server answer: " << response << endl;
    }

    // Close TCP connection
    close(socket);

    return 0;
}
