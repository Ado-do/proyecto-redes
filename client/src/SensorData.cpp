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
         << "'humidity': " << humidity << "}"
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

    SensorData sd{id++, temp_distr(gen), press_distr(gen), hum_distr(gen)};
    return sd;
}


