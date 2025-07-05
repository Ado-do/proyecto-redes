CC = g++
CFLAGS = -std=c++17 -Wall -lssl -lcrypto
LD_LIBS = -lssl -lcrypto

SRC = $(wildcard src/*.cpp)
OBJ = $(SRC:src/%.cpp=build/%.o)

TARGET = build/sensor_client


all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) -o $@ $^ $(LD_LIBS)

build/%.o: src/%.cpp
	@mkdir -p build/
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf build/
