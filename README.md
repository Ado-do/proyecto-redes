# Proyecto Semestral - Redes de Computadores 2025-S1

## Descripción

Sistema distribuido IoT para monitoreo industrial con clientes C++, servidores Python y visualización web.

## Uso

### Requerimientos

- Linux
- Compilador C++, librería OpenSSL, GNU Make y git.
- Python 3.11+
- Librería OpenSSL
- GNU Make
- Git

> [!TIP]
> Puedes instalar todos utilizando:
>
> - En Debian/Ubuntu: `sudo apt install g++ make git python3 libssl-dev`
> - En Red Hat/Fedora: `sudo dnf install gcc-c++ make git python3 openssl-devel`

### Comandos

Para probar cada parte del proyecto, primero necesitaras clonar y configurar el repositorio:

```bash
# Clonar repositorio
git clone https://github.com/Ado-do/proyecto-redes

# Acceder a repo
cd proyecto-redes/

# Generar certificados TLS
./gen_tls_certs.sh

# Recrear python virtual environment
./setup_venv.sh
```

Luego, necesitaras 4 terminales abiertas para ejecutar cada modulo del proyecto:

**Terminal 1**: Ejecutar servidor final:

```bash
# Activar python venv
source .venv/bin/activate

# Ejecutar servidor final
uvicorn final_server.main:app

# Visualizar datos enviados en navegador
xdg-open http://localhost:8000/api/dashboard
```

**Terminal 2**: Ejecutar servidor medio

```bash
# Activar python venv
source .venv/bin/activate

# Ejecutar servidor medio
python ./mid_server/main.py
```

**Terminal 3**: Ejecutar cliente de consultas

```bash
# Activar python venv
source .venv/bin/activate

# Ejecutar cliente de consultas
python ./query_client/main.py
```

**Terminal 4**: Ejecutar cliente de sensor (enviar datos de prueba de sensores) y visualizar resultados

```bash
# Compilar código de cliente sensor
make -C client/

# Enviar datos de sensor al servidor medio cada 5 segundos
watch -n 5 ./client/build/sensor_client
```
