#pragma once

#include <cstdint>

// temperature, pressure, humidity are float casted to ints * 100
struct SensorData {
    int16_t id;
    int32_t temperature;
    int32_t pressure;
    int32_t humidity;
    uint16_t checksum;

    void print_data();
} __attribute__((packed)); // Disable padding

SensorData create_fake_sensor_data();
uint16_t compute_checksum(const SensorData& data);
