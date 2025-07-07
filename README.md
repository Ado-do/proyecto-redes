# Proyecto Semestral - Redes de Computadores 2025-S1

## Descripción

Sistema distribuido IoT para monitoreo industrial con clientes C++, servidores Python y visualización web.

## Uso

### Requerimientos

- Compilador C++ (GNU g++)
  - Librería OpenSSL
- GNU Make
- Python 3.9+
  - Librerias: `pip install fastapi uvicorn sqlite requests crcmod`

### Comandos

```bash
# Generar certificados
./gen_certs.bash

# Compilar y ejecutar cliente
make -C client/
./client/build/sensor_client

# Ejecutar servidor medio
python ./mid_server/main.py

# Ejecutar servidor final
uvicorn final_server.main:app

# Ejecutar cliente de consulta
python ./query_client/main.py
```
