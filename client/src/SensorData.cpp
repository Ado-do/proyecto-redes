#include "SensorData.hpp"

#include <iostream>
#include <iomanip>
#include <random>

using namespace std;

void SensorData::print_data() {
    cout << fixed << setprecision(2) << "SensorData: {"
         << "'id': " << id << ", "
         << "'temperature': " << temperature << ", "
         << "'pressure': " << pressure << ", "
         << "'humidity': " << humidity << ", "
         << "'checksum': " << (uint16_t)checksum << "}"
         << endl;
}


// Create random fake sensor data
SensorData create_fake_sensor_data() {
    static int16_t id = 0;
    static random_device rd;
    static mt19937 gen(rd());

    uniform_real_distribution<float> temp_distr(-50, 150);
    uniform_real_distribution<float> press_distr(300, 1200);
    uniform_real_distribution<float> hum_distr(0, 100);

    SensorData sd = {
        id++,
        static_cast<int32_t>(temp_distr(gen) * 100),
        static_cast<int32_t>(press_distr(gen) * 100),
        static_cast<int32_t>(hum_distr(gen) * 100),
    };
    sd.checksum = compute_checksum(sd);

    return sd;
}

// Simple CRC-16 checksum TODO: FIX THIS WEA
uint16_t compute_checksum(const SensorData& data) {
    // treat data as sequence of bits
    const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&data);
    uint16_t crc = 0xFFFF;

    // iterate bits of data, without the last two bits (checksum field)
    // for (size_t i = 0; i < sizeof(data) - sizeof(data.checksum); i++) { // More readable
    for (size_t i = 0; i < sizeof(SensorData) - sizeof(uint16_t); i++) {
        crc ^= bytes[i];
        for (int j = 0; j < 8; j++) {
            bool lsb = crc & 0x0001;
            crc >>= 1;
            if (lsb) crc ^= 0xA001;
        }
    }
    return crc;
}
