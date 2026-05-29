##############################################################################
#
#
##############################################################################
# analisis.py - Servicio de Analítica
import zmq
import json
import time
import threading
from datetime import datetime
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

# Variables compartidas con lock para seguridad en multihilos
lock = threading.Lock()
db_primary_active = True
congestion_history = {}

print("[ANALÍTICA] Servicio de analítica activo...")
print("[ANALÍTICA] Modo: MULTIHILOS")
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
    
    with lock:
        # Simular fallo de BD principal a los 140s
        if elapsed >= DB_FAILURE_TIME and db_primary_active:
            db_primary_active = False
            print(f"\n[ANALÍTICA] [FALLO] FALLO DE BD PRINCIPAL EN PC3 DETECTADO ({elapsed:.1f}s)")
            print(f"[ANALÍTICA] [CAMBIO] Cambiando a BD RÉPLICA en PC2\n")
        
        # Enviar a la BD que esté activa
        if db_primary_active:
            try:
                push_db.send_json(evento)
            except Exception as e:
                print(f"[ANALÍTICA] [ERROR] Fallo al guardar en BD principal: {e}, usando réplica")
                push_db_r.send_json(evento)
        else:
            # BD principal falla, usar réplica
            try:
                push_db_r.send_json(evento)
            except Exception as e:
                print(f"[ANALÍTICA] [ERROR] Fallo al guardar en BD réplica: {e}")

def listener_sensores():
    """Thread que escucha eventos de sensores"""
    while True:
        try:
            msg = sub_socket.recv_string()
            topic, data = msg.split(" ", 1)
            evento = json.loads(data)
            timestamp_legible = evento.get("timestamp_legible", "N/A")
            elapsed = get_elapsed_time()
            
            if topic == "ambulancia":
                # Evento de ambulancia
                print(f"\n[ANALÍTICA] [{timestamp_legible}] [EMERGENCIA] AMBULANCIA DETECTADA A LOS {elapsed:.1f}s")
                print(f"[ANALÍTICA]    Sensor ID: {evento.get('sensor_id', 'N/A')}")
                print(f"[ANALÍTICA]    Fila: {evento['fila']}")
                print(f"[ANALÍTICA]    Motivo: {evento['motivo']}")
                print(f"[ANALÍTICA]    Prioridad: {evento.get('prioridad', 'N/A')}")
                print(f"[ANALÍTICA]    Intersecciones: {', '.join(evento['intersecciones'])}")
                print(f"[ANALÍTICA]    Acción: VERDE PRIORITARIO en toda la Fila {evento['fila']}\n")
                
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
                        "prioridad": "CRITICA",
                        "timestamp_legible": timestamp_legible
                    })
            else:
                # Eventos de sensores
                estado = evaluar_sensor(topic, evento)
                evento["estado"] = estado
                evento["topic"] = topic
                
                sensor_id = evento.get('sensor_id', 'N/A')
                interseccion = evento.get('interseccion', 'N/A')
                
                print(f"[{timestamp_legible}] [SENSOR] {topic.upper()}: {sensor_id} en {interseccion} -> {estado}")
                
                # Guardar en BD
                save_to_db(evento)
                
                # Tomar decisión sobre semáforo
                if estado == "CONGESTION":
                    print(f"[{timestamp_legible}] [CONGESTION] Detectada en {interseccion} por {topic}")
                    push_traffic.send_json({
                        "accion": "EXTENDER_VERDE",
                        "interseccion": evento["interseccion"],
                        "motivo": f"Congestión detectada por {topic}",
                        "duracion_extra": 10,
                        "timestamp_legible": timestamp_legible
                    })
        except Exception as e:
            print(f"[ANALÍTICA] [ERROR] Error en listener_sensores: {e}")
            time.sleep(0.1)

def listener_consultas():
    """Thread que escucha consultas desde PC3"""
    while True:
        try:
            query = query_socket.recv_json()
            query_type = query.get('tipo', 'desconocida')
            timestamp_legible = query.get('timestamp_legible', 'N/A')
            origen = query.get('origen', 'N/A')
            
            if query_type == "estado_general":
                print(f"\n[ANALÍTICA] [{timestamp_legible}] [CONSULTA] Estado General solicitado desde {origen}")
                print(f"[ANALÍTICA]    - Tipo: {query_type}")
                print(f"[ANALÍTICA]    - Origen: {origen}\n")
            
            elif query_type == "eventos_congestion":
                ventana_tiempo = query.get('parametros', {}).get('tiempo_ventana', 'N/A')
                print(f"\n[ANALÍTICA] [{timestamp_legible}] [CONSULTA] Eventos de Congestión solicitado desde {origen}")
                print(f"[ANALÍTICA]    - Tipo: {query_type}")
                print(f"[ANALÍTICA]    - Ventana de tiempo: {ventana_tiempo}s")
                print(f"[ANALÍTICA]    - Origen: {origen}\n")
            
            elif query_type == "comando_directo_semaforo":
                interseccion = query.get('interseccion', 'N/A')
                accion = query.get('accion', 'N/A')
                duracion = query.get('duracion', 'N/A')
                print(f"\n[ANALÍTICA] [{timestamp_legible}] [COMANDO] Comando de Usuario desde {origen}")
                print(f"[ANALÍTICA]    - Intersección: {interseccion}")
                print(f"[ANALÍTICA]    - Acción: {accion}")
                print(f"[ANALÍTICA]    - Duración: {duracion}s\n")
                
                # Procesar comando de semáforo
                push_traffic.send_json({
                    "accion": accion,
                    "interseccion": interseccion,
                    "motivo": "Comando directo de usuario desde PC3",
                    "duracion": duracion,
                    "timestamp_legible": timestamp_legible
                })
            else:
                print(f"\n[ANALÍTICA] [{timestamp_legible}] [CONSULTA] Tipo desconocido: {query_type}")
                print(f"[ANALÍTICA]    Datos: {json.dumps(query, indent=2)}\n")
        
        except Exception as e:
            print(f"[ANALÍTICA] [ERROR] Error en listener_consultas: {e}")
            time.sleep(0.1)

# Crear y lanzar threads
thread_sensores = threading.Thread(target=listener_sensores, daemon=True)
thread_consultas = threading.Thread(target=listener_consultas, daemon=True)

thread_sensores.start()
thread_consultas.start()

print("[ANALÍTICA] Threads iniciados: sensores y consultas\n")

# Mantener el programa activo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[ANALÍTICA] Finalizando servicio...")


