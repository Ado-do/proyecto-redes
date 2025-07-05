#pragma once

#include <cstdint>

struct SensorData {
    int16_t id;
    float temperature;
    float pressure;
    float humidity;

    void print_data();
} __attribute__((packed)); // Disable padding (14 bytes)

// Create random fake sensor data
SensorData create_fake_sensor_data();
