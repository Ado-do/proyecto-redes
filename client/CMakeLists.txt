cmake_minimum_required(VERSION 3.10)
project(SensorClient)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find OpenSSL package for TLS support
find_package(OpenSSL REQUIRED)

# Include directories
include_directories(
    ${PROJECT_SOURCE_DIR}/src
)

# Source files
set(SOURCES
    src/main.cpp
    src/SensorData.cpp
)

# Executable target
add_executable(sensor_client ${SOURCES})

# Link libraries
target_link_libraries(sensor_client PRIVATE
    OpenSSL::SSL
    OpenSSL::Crypto
)

# Installation (optional)
# install(TARGETS sensor_client DESTINATION bin)

# Build options
# option(BUILD_TESTS "Build tests" OFF)
# if(BUILD_TESTS)
#     enable_testing()
#     # Add your test configuration here
# endif()

# Print configuration summary
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Source directory: ${PROJECT_SOURCE_DIR}")
message(STATUS "Binary directory: ${PROJECT_BINARY_DIR}")
