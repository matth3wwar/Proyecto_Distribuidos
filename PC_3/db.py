# db.py - Base de datos principal en PC3
import zmq
import json
import time
from config import DB_BIND_ADDRESS, DB_FAILURE_TIME

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(DB_BIND_ADDRESS)

print("[DB PRINCIPAL PC3] Base de datos principal activa...")
print(f"[DB PRINCIPAL PC3] Simulando fallo a los {DB_FAILURE_TIME}s...\n")

start_time = time.time()
failed = False

def get_elapsed_time():
    return time.time() - start_time

while True:
    elapsed = get_elapsed_time()
    
    # Simular fallo de BD a los 140s
    if elapsed >= DB_FAILURE_TIME and not failed:
        failed = True
        print(f"\n[{elapsed:.1f}s] FALLO DE BD PRINCIPAL EN PC3 - {DB_FAILURE_TIME}s alcanzado")
        print(f"[{elapsed:.1f}s] BD PRINCIPAL OFFLINE - Usando BD RÉPLICA en PC2\n")
        continue
    
    if failed:
        # Silenciosamente rechazar nuevas peticiones
        try:
            socket.recv_json(zmq.NOBLOCK)
        except zmq.Again:
            pass
        time.sleep(0.1)
        continue
    
    try:
        data = socket.recv_json(zmq.NOBLOCK)
        evento_tipo = data.get("tipo_sensor", "desconocido")
        interseccion = data.get("interseccion", "DESCONOCIDA")
        estado = data.get("estado", "DESCONOCIDO")
        
        print(f"[{elapsed:.1f}s] [DB PRINCIPAL] Guardando evento: {evento_tipo} en {interseccion} -> {estado}")
        
        # Guardar en db.json
        with open("db.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except zmq.Again:
        pass
    
    time.sleep(0.01)
