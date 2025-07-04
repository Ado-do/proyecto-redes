# Después de parse_sensor_data
def verify_data(data: dict) -> bool:
    # Simula verificación (luego implementarás cifrado real)
    return all([
        -50 <= data["temperatura"] <= 150,
        300 <= data["presion"] <= 1200,
        0 <= data["humedad"] <= 100
    ])

# Modifica el bloque principal:
if verify_data(sensor_data):
    conn.sendall(b"ACK")  # Confirmación
else:
    conn.sendall(b"ERR")
