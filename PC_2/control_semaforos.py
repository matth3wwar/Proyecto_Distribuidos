#######################################################################################
#
#
###################################################################################
# control_semaforos.py - Control de semáforos
import zmq
import time
import json
from datetime import datetime
from config import TRAFFIC_BIND_ADDRESS, NORMAL_GREEN_TIME, DB_PUSH_ADDRESS, DB_REPLICA_PUSH_ADDRESS

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(TRAFFIC_BIND_ADDRESS)

# Sockets para guardar cambios en la BD
db_socket = context.socket(zmq.PUSH)
db_socket.connect(DB_PUSH_ADDRESS)

db_replica_socket = context.socket(zmq.PUSH)
db_replica_socket.connect(DB_REPLICA_PUSH_ADDRESS)

print("[SEMÁFOROS] Control de semáforos activo...")
print(f"[SEMÁFOROS] Tiempo verde normal: {NORMAL_GREEN_TIME}s\n")

estados = {}
start_time = time.time()

def get_elapsed_time():
    return time.time() - start_time

def guardar_cambio_semaforo(interseccion, estado, accion, comando):
    """Guarda el cambio de estado del semáforo en la base de datos"""
    timestamp = comando.get("timestamp", time.time())
    timestamp_legible = comando.get("timestamp_legible", datetime.fromtimestamp(timestamp).isoformat())
    motivo = comando.get("motivo", "")
    prioridad = comando.get("prioridad", "NORMAL")
    
    evento = {
        "tipo_sensor": "semaforo",
        "interseccion": interseccion,
        "estado": estado,
        "accion": accion,
        "timestamp": timestamp,
        "timestamp_legible": timestamp_legible,
        "sensor_id": f"SEMAFORO_{interseccion}",
        "motivo": motivo,
        "prioridad": prioridad
    }
    
    # Agregar duraciones si existen
    if accion == "EXTENDER_VERDE":
        evento["duracion_extra"] = comando.get("duracion_extra", 10)
    elif accion == "CAMBIAR_A_VERDE" or accion == "VERDE":
        evento["duracion"] = comando.get("duracion", NORMAL_GREEN_TIME)
    
    # Enviar a BD principal y réplica
    try:
        db_socket.send_json(evento, zmq.NOBLOCK)
        db_replica_socket.send_json(evento, zmq.NOBLOCK)
    except zmq.Again:
        pass

while True:
    comando = socket.recv_json()
    
    elapsed = get_elapsed_time()
    interseccion = comando.get("interseccion", "DESCONOCIDA")
    accion = comando.get("accion", "DESCONOCIDA")
    motivo = comando.get("motivo", "")
    prioridad = comando.get("prioridad", "NORMAL")
    timestamp_legible = comando.get("timestamp_legible", "N/A")
    
    print(f"\n[{timestamp_legible}] [SEMÁFOROS] Comando para {interseccion}:")
    
    if accion == "VERDE_AMBULANCIA":
        estados[interseccion] = "VERDE_AMBULANCIA"
        print(f"[{timestamp_legible}]    [OK] Estado: VERDE PRIORITARIO (AMBULANCIA)")
        print(f"[{timestamp_legible}]    [OK] Prioridad: {prioridad}")
        print(f"[{timestamp_legible}]    [OK] Motivo: {motivo}\n")
        guardar_cambio_semaforo(interseccion, "VERDE_AMBULANCIA", accion, comando)
    
    elif accion == "EXTENDER_VERDE":
        duracion_extra = comando.get("duracion_extra", 10)
        estados[interseccion] = "VERDE_EXTENDIDO"
        print(f"[{timestamp_legible}]    [OK] Estado: VERDE_EXTENDIDO ({NORMAL_GREEN_TIME}s + {duracion_extra}s extra)")
        print(f"[{timestamp_legible}]    [OK] Motivo: {motivo}\n")
        guardar_cambio_semaforo(interseccion, "VERDE_EXTENDIDO", accion, comando)
    
    elif accion == "CAMBIAR_A_VERDE" or accion == "VERDE":
        duracion = comando.get("duracion", NORMAL_GREEN_TIME)
        estados[interseccion] = "VERDE"
        print(f"[{timestamp_legible}]    [OK] Estado: VERDE")
        print(f"[{timestamp_legible}]    [OK] Duración: {duracion}s")
        print(f"[{timestamp_legible}]    [OK] Motivo: {motivo}\n")
        guardar_cambio_semaforo(interseccion, "VERDE", accion, comando)
    
    else:
        estados[interseccion] = "ROJO"
        print(f"[{timestamp_legible}]    [OK] Estado: ROJO\n")
        guardar_cambio_semaforo(interseccion, "ROJO", accion, comando)
