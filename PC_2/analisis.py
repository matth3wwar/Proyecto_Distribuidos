##############################################################################
#
#
##############################################################################
# analisis.py - Servicio de Analítica
import zmq
import json
import time
from config import (ANALYTICS_SUB_ADDRESS, DB_PUSH_ADDRESS, DB_REPLICA_PUSH_ADDRESS, 
                    TRAFFIC_PUSH_ADDRESS, QUERY_BIND_ADDRESS, DB_FAILURE_TIME)

context = zmq.Context()

# broker
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(ANALYTICS_SUB_ADDRESS)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "camara")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "espira")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "gps")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "ambulancia")

# BD principal
push_db = context.socket(zmq.PUSH)
push_db.connect(DB_PUSH_ADDRESS)

# BD replica
push_db_r = context.socket(zmq.PUSH)
push_db_r.connect(DB_REPLICA_PUSH_ADDRESS)

# Control de semáforos
push_traffic = context.socket(zmq.PUSH)
push_traffic.connect(TRAFFIC_PUSH_ADDRESS)

# Query responses (para responder consultas desde PC3)
query_socket = context.socket(zmq.PULL)
query_socket.bind(QUERY_BIND_ADDRESS)

start_time = time.time()
db_primary_active = True
congestion_history = {}

print("[ANALÍTICA] Servicio de analítica activo...")
print("[ANALÍTICA] Esperando eventos de sensores y ambulancias...\n")

def get_elapsed_time():
    return time.time() - start_time

def evaluar_sensor(topic, evento):
    """Evalúa si hay congestión basado en reglas de sensores"""
    if topic == "camara":
        if evento["volumen"] > 8 or evento["velocidad_promedio"] < 15:
            return "CONGESTION"
        return "NORMAL"

    if topic == "espira":
        if evento["vehiculos_contados"] > 15:
            return "CONGESTION"
        return "NORMAL"

    if topic == "gps":
        if evento["velocidad_promedio"] < 10:
            return "CONGESTION"
        return "NORMAL"

    return "NORMAL"

def save_to_db(evento):
    """Guarda evento en BD, considerando si la principal está activa"""
    global db_primary_active
    elapsed = get_elapsed_time()
    
    # Simular fallo de BD principal a los 140s
    if elapsed >= DB_FAILURE_TIME and db_primary_active:
        db_primary_active = False
        print(f"\n[ANALÍTICA] FALLO DE BD PRINCIPAL EN PC3 DETECTADO ({elapsed:.1f}s)")
        print(f"[ANALÍTICA] Cambiando a BD RÉPLICA en PC2\n")
    
    if db_primary_active:
        try:
            push_db.send_json(evento)
        except:
            print("[ANALÍTICA] ⚠️  Fallo al guardar en BD principal, usando réplica")
    else:
        push_db_r.send_json(evento)

# Poller para recibir mensajes de sensores y consultas
poller = zmq.Poller()
poller.register(sub_socket, zmq.POLLIN)
poller.register(query_socket, zmq.POLLIN)

while True:
    elapsed = get_elapsed_time()
    
    # Poll con timeout de 1000ms para no bloquear
    events = poller.poll(1000)
    
    for socket_obj, event_type in events:
        if socket_obj == sub_socket:
            msg = sub_socket.recv_string()
            topic, data = msg.split(" ", 1)
            evento = json.loads(data)
            
            if topic == "ambulancia":
                # Evento de ambulancia - MÁXIMA PRIORIDAD
                print(f"\n[ANALÍTICA] AMBULANCIA DETECTADA A LOS {elapsed:.1f}s")
                print(f"[ANALÍTICA]    Fila: {evento['fila']}")
                print(f"[ANALÍTICA]    Motivo: {evento['motivo']}")
                print(f"[ANALÍTICA]    Acción: VERDE PRIORITARIO en intersecciones de Fila {evento['fila']}\n")
                
                # Guardar evento
                evento["estado"] = "EMERGENCIA"
                evento["topic"] = topic
                save_to_db(evento)
                
                # Enviar comandos a semáforos
                for interseccion in evento['intersecciones']:
                    push_traffic.send_json({
                        "accion": "VERDE_AMBULANCIA",
                        "interseccion": interseccion,
                        "motivo": f"Ambulancia solicitando paso - {evento['motivo']}",
                        "prioridad": "CRITICA"
                    })
            else:
                # Eventos de sensores
                estado = evaluar_sensor(topic, evento)
                evento["estado"] = estado
                evento["topic"] = topic
                
                print(f"[{elapsed:.1f}s] Analítica procesó {topic}: {evento['interseccion']} -> {estado}")
                
                # Guardar en BD
                save_to_db(evento)
                
                # Tomar decisión sobre semáforo
                if estado == "CONGESTION":
                    print(f"[{elapsed:.1f}s] CONGESTION detectada en {evento['interseccion']}")
                    push_traffic.send_json({
                        "accion": "EXTENDER_VERDE",
                        "interseccion": evento["interseccion"],
                        "motivo": f"Congestión detectada por {topic}",
                        "duracion_extra": 10
                    })
        
        elif socket_obj == query_socket:
            # Responder a consultas desde PC3
            try:
                query = query_socket.recv_json(zmq.NOBLOCK)
                print(f"\n[ANALÍTICA] 📊 Consulta recibida desde PC3: {query.get('tipo', 'desconocida')}")
                # Aquí se pueden procesar diferentes tipos de consultas
            except zmq.Again:
                pass

