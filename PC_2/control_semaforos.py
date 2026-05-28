#######################################################################################
#
#
###################################################################################
# control_semaforos.py - Control de semáforos
import zmq
import time
from config import TRAFFIC_BIND_ADDRESS, NORMAL_GREEN_TIME

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(TRAFFIC_BIND_ADDRESS)

print("[SEMÁFOROS] Control de semáforos activo...")
print(f"[SEMÁFOROS] Tiempo verde normal: {NORMAL_GREEN_TIME}s\n")

estados = {}
start_time = time.time()

def get_elapsed_time():
    return time.time() - start_time

while True:
    comando = socket.recv_json()
    
    elapsed = get_elapsed_time()
    interseccion = comando.get("interseccion", "DESCONOCIDA")
    accion = comando.get("accion", "DESCONOCIDA")
    motivo = comando.get("motivo", "")
    prioridad = comando.get("prioridad", "NORMAL")
    
    print(f"[{elapsed:.1f}s] [SEMAFOROS] Comando para {interseccion}:")
    
    if accion == "VERDE_AMBULANCIA":
        estados[interseccion] = "VERDE_AMBULANCIA"
        print(f"[{elapsed:.1f}s]    [OK] Estado: VERDE PRIORITARIO (AMBULANCIA)")
        print(f"[{elapsed:.1f}s]    [OK] Motivo: {motivo}\n")
    
    elif accion == "EXTENDER_VERDE":
        duracion_extra = comando.get("duracion_extra", 10)
        estados[interseccion] = "VERDE_EXTENDIDO"
        print(f"[{elapsed:.1f}s]    [OK] Estado: VERDE_EXTENDIDO ({NORMAL_GREEN_TIME}s + {duracion_extra}s extra)")
        print(f"[{elapsed:.1f}s]    [OK] Motivo: {motivo}\n")
    
    elif accion == "CAMBIAR_A_VERDE":
        estados[interseccion] = "VERDE"
        print(f"[{elapsed:.1f}s]    [OK] Estado: VERDE")
        print(f"[{elapsed:.1f}s]    [OK] Motivo: {motivo}\n")
    
    else:
        estados[interseccion] = "ROJO"
        print(f"[{elapsed:.1f}s]    ✓ Estado: ROJO\n")
