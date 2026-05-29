####################################################################################
#
# db_replica.py - Base de datos réplica en PC2
####################################################################################

import zmq
import json
import time
from config import DB_REPLICA_BIND_ADDRESS

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(DB_REPLICA_BIND_ADDRESS)

print("[DB RÉPLICA PC2] Base de datos réplica activa...")
print("[DB RÉPLICA PC2] Guardando datos de eventos...\n")

start_time = time.time()

def get_elapsed_time():
    return time.time() - start_time

while True:
    data = socket.recv_json()
    elapsed = get_elapsed_time()
    
    evento_tipo = data.get("tipo_sensor", "desconocido")
    interseccion = data.get("interseccion", "DESCONOCIDA")
    estado = data.get("estado", "DESCONOCIDO")
    timestamp_legible = data.get("timestamp_legible", "N/A")
    sensor_id = data.get("sensor_id", "N/A")
    
    print(f"[{timestamp_legible}] [DB RÉPLICA] {evento_tipo.upper()}: {sensor_id} en {interseccion} -> {estado}")
    
    # Guardar en db_replica.json
    with open("db_replica.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")
