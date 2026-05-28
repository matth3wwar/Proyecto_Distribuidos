# consultas.py - Módulo de consultas desde PC3 al servicio de analítica en PC2
import zmq
import json
import time
from config import QUERY_PULL_ADDRESS

context = zmq.Context()

# Socket PUSH para enviar consultas al servicio de analítica
push_socket = context.socket(zmq.PUSH)
push_socket.connect(QUERY_PULL_ADDRESS)

print("[CONSULTAS PC3] Módulo de consultas activo...")
print("[CONSULTAS PC3] Conectado al servicio de analítica en PC2\n")

start_time = time.time()

def get_elapsed_time():
    return time.time() - start_time

def enviar_consulta(tipo_consulta, parametros=None):
    """Envía una consulta al servicio de analítica"""
    consulta = {
        "tipo": tipo_consulta,
        "parametros": parametros or {},
        "timestamp": time.time(),
        "origen": "PC3_CONSULTAS"
    }
    
    try:
        push_socket.send_json(consulta)
        elapsed = get_elapsed_time()
        print(f"[{elapsed:.1f}s] [CONSULTAS] [OK] Consulta enviada: {tipo_consulta}")
        return True
    except Exception as e:
        elapsed = get_elapsed_time()
        print(f"[{elapsed:.1f}s] [CONSULTAS] [ERROR] Error al enviar consulta: {e}")
        return False

def enviar_comando_semaforo(interseccion, accion, duracion=None):
    """Envía un comando directo para cambiar estado de un semáforo"""
    comando = {
        "tipo": "comando_directo_semaforo",
        "interseccion": interseccion,
        "accion": accion,
        "duracion": duracion,
        "timestamp": time.time(),
        "origen": "PC3_USUARIO"
    }
    
    elapsed = get_elapsed_time()
    print(f"[{elapsed:.1f}s] [CONSULTAS] [COMANDO] Comando directo de usuario: {interseccion} -> {accion}")
    
    try:
        push_socket.send_json(comando)
        return True
    except Exception as e:
        print(f"[{elapsed:.1f}s] [CONSULTAS] [ERROR] Error al enviar comando: {e}")
        return False

# Simular consultas periódicas
while True:
    elapsed = get_elapsed_time()
    
    # Enviar consulta de estado general cada 30 segundos
    if int(elapsed) % 30 == 0 and elapsed > 0:
        enviar_consulta("estado_general")
    
    # Enviar consulta de congestiones cada 45 segundos
    if int(elapsed) % 45 == 0 and elapsed > 20:
        enviar_consulta("eventos_congestion", {"tiempo_ventana": 10})
    
    # Enviar comando directo de usuario en tiempo 80 seg
    if 80 <= elapsed <= 81:
        enviar_comando_semaforo("INT_1b", "VERDE", duracion=20)
    
    time.sleep(1)
