#include "SensorData.hpp"

#include <iostream>
#include <iomanip>
#include <random>

using namespace std;

const int TEMP_MIN = -50;
const int TEMP_MAX = 150;

const int PRESS_MIN = 300;
const int PRESS_MAX = 1200;

const int HUM_MIN = 0;
const int HUM_MAX = 100;

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

    uniform_real_distribution<float> temp_distr(TEMP_MIN, TEMP_MAX);
    uniform_real_distribution<float> press_distr(PRESS_MIN, PRESS_MAX);
    uniform_real_distribution<float> hum_distr(HUM_MIN, HUM_MAX);

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
    const uint16_t poly = 0xA001; // equal to x^16 + x^15 + x^2 + 1
    uint16_t crc = 0xFFFF;

    // iterate bits of data, without the last two bits (checksum field)
    for (size_t i = 0; i < sizeof(data) - sizeof(data.checksum); i++) { // More readable
        crc ^= bytes[i];
        for (int j = 0; j < 8; j++) {
            bool lsb = crc & 0x0001;
            crc >>= 1;
            if (lsb) crc ^= poly;
        }
    }
    return crc;
}
