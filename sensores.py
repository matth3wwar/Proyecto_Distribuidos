##############################################################################
#
# sensores.py - Generador de eventos de sensores
################################################################################
import zmq
import time
import json
import random
from datetime import datetime
from config import BROKER_SUB_ADDRESS, INTERSECCIONES, SENSOR_INTERVAL

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(BROKER_SUB_ADDRESS)

start_time = time.time()
congestion_b2_sent = False
congestion_d3_sent = False
ambulance_1_sent = False
ambulance_2_sent = False

def get_elapsed_time():
    return time.time() - start_time

def generate_camera_event(interseccion, congestion_level=0):
    """
    congestion_level: 0 = normal, 1 = high congestion
    """
    if congestion_level > 0:
        volumen = random.randint(0, 15)
        velocidad = random.randint(10, 50)
    else:
        volumen = random.randint(0, 8)
        velocidad = random.randint(20, 60)
    
    timestamp_unix = time.time()
    timestamp_legible = datetime.fromtimestamp(timestamp_unix).isoformat()
    print(f"[SENSORES] prioridad=CRITICA | timestamp={timestamp_unix} | timestamp_legible={timestamp_legible}")
    return {
        "sensor_id": f"CAM-{interseccion}",
        "tipo_sensor": "camara",
        "interseccion": interseccion,
        "volumen": volumen,
        "velocidad_promedio": velocidad,
        "timestamp": timestamp_unix,
        "timestamp_legible": timestamp_legible
    }

def generate_espira_event(interseccion, congestion_level=0):
    """
    congestion_level: 0 = normal, 1 = high congestion
    """
    inicio = time.time()
    if congestion_level > 0:
        vehiculos = random.randint(18, 25)
    else:
        vehiculos = random.randint(5, 20)
    timestamp_unix = time.time()
    timestamp_legible = datetime.fromtimestamp(timestamp_unix).isoformat()
    print(f"[SENSORES] prioridad=CRITICA | timestamp={timestamp_unix} | timestamp_legible={timestamp_legible}")
    return {
        "sensor_id": f"ESP-{interseccion}",
        "tipo_sensor": "espira_inductiva",
        "interseccion": interseccion,
        "vehiculos_contados": vehiculos,
        "intervalo_segundos": 30,
        "timestamp_inicio": inicio,
        "timestamp_fin": inicio + 30,
        "timestamp_legible": timestamp_legible
    }

def generate_gps_event(interseccion, congestion_level=0):
    """
    congestion_level: 0 = normal, 1 = high congestion
    """
    if congestion_level > 0:
        velocidad = random.randint(2, 8)
        nivel = "BAJA"
    else:
        velocidad = random.randint(20, 50)
        nivel = "ALTA" if velocidad > 40 else ("NORMAL" if velocidad >= 20 else "BAJA")

    timestamp_unix = time.time()
    timestamp_legible = datetime.fromtimestamp(timestamp_unix).isoformat()
    print(f"[SENSORES] prioridad=CRITICA | timestamp={timestamp_unix} | timestamp_legible={timestamp_legible}")
    
    return {
        "sensor_id": f"GPS-{interseccion}",
        "tipo_sensor": "gps",
        "interseccion": interseccion,
        "nivel_congestion": nivel,
        "velocidad_promedio": velocidad,
        "timestamp": timestamp_unix,
        "timestamp_legible": timestamp_legible
    }

def generate_ambulance_event(fila, motivo="emergencia medica"):
    """
    Genera un evento de ambulancia solicitando paso en una fila específica
    """
    intersecciones_fila = [f"INT_{fila}a", f"INT_{fila}b", f"INT_{fila}c", f"INT_{fila}d", f"INT_{fila}e"]
    timestamp_unix = time.time()
    timestamp_legible = datetime.fromtimestamp(timestamp_unix).isoformat()
    
    return {
        "sensor_id": f"AMBULANCIA-{fila}",
        "tipo_sensor": "ambulancia",
        "fila": fila,
        "intersecciones": intersecciones_fila,
        "motivo": motivo,
        "prioridad": "CRITICA",
        "timestamp": timestamp_unix,
        "timestamp_legible": timestamp_legible
    }

elapsed = 0
iteration = 0

print(f"[SENSORES] Iniciando simulación de ciudad 3x5...")
print(f"[SENSORES] Congestión esperada en INT_2b a los 60s, INT_3d a los 95s")
print(f"[SENSORES] Ambulancia fila 1 a los 130s, fila 1 a los 150s")
print(f"[SENSORES] Fallo de BD en PC3 a los 140s\n")

while True:
    elapsed = get_elapsed_time()
    iteration += 1
    
    # Generar eventos de sensores en intersecciones aleatorias
    if elapsed < 60 or (60 < elapsed < 95) or (95 < elapsed < 130) or elapsed > 150:
        # Tráfico normal
        interseccion = random.choice(INTERSECCIONES)
        tipo = random.choice(["camara", "espira", "gps"])
        congestion = 0
    elif 60 <= elapsed <= 75:
        # Congestión en INT_2b (b2)
        interseccion = "INT_2b"
        tipo = random.choice(["camara", "espira", "gps"])
        congestion = 1
    elif 95 <= elapsed <= 110:
        # Congestión en INT_3d (d3)
        interseccion = "INT_3d"
        tipo = random.choice(["camara", "espira", "gps"])
        congestion = 1
    else:
        interseccion = random.choice(INTERSECCIONES)
        tipo = random.choice(["camara", "espira", "gps"])
        congestion = 0

    if tipo == "camara":
        event = generate_camera_event(interseccion, congestion)
        topic = "camara"
    elif tipo == "espira":
        event = generate_espira_event(interseccion, congestion)
        topic = "espira"
    else:
        event = generate_gps_event(interseccion, congestion)
        topic = "gps"

    socket.send_string(topic + " " + json.dumps(event))
    
    # Mostrar detalles del evento en consola
    timestamp_legible = event.get("timestamp_legible", "N/A")
    sensor_id = event.get("sensor_id", "N/A")
    
    if topic == "camara":
        volumen = event.get("volumen", "N/A")
        velocidad = event.get("velocidad_promedio", "N/A")
        print(f"[{timestamp_legible}] [SENSOR] CAMARA: {sensor_id} en {interseccion} - Volumen: {volumen}, Velocidad: {velocidad} km/h")
    elif topic == "espira":
        vehiculos = event.get("vehiculos_contados", "N/A")
        print(f"[{timestamp_legible}] [SENSOR] ESPIRA: {sensor_id} en {interseccion} - Vehículos: {vehiculos}")
    elif topic == "gps":
        velocidad = event.get("velocidad_promedio", "N/A")
        nivel = event.get("nivel_congestion", "N/A")
        print(f"[{timestamp_legible}] [SENSOR] GPS: {sensor_id} en {interseccion} - Velocidad: {velocidad} km/h, Nivel: {nivel}")
    
    # Primera ambulancia en fila 1 a los 130s
    if 130 <= elapsed <= 132 and not ambulance_1_sent:
        ambulance_event = generate_ambulance_event("1", "Emergencia médica - Ambulancia 1")
        socket.send_string("ambulancia " + json.dumps(ambulance_event))
        timestamp_legible = ambulance_event.get("timestamp_legible", "N/A")
        sensor_id = ambulance_event.get("sensor_id", "N/A")
        fila = ambulance_event.get("fila", "N/A")
        motivo = ambulance_event.get("motivo", "N/A")
        intersecciones = ", ".join(ambulance_event.get("intersecciones", []))
        print(f"\n[{timestamp_legible}] [AMBULANCIA] {sensor_id} - Fila: {fila}, Motivo: {motivo}")
        print(f"[{timestamp_legible}]              Intersecciones: {intersecciones}\n")
        ambulance_1_sent = True
    
    # Segunda ambulancia en fila 1 a los 150s
    if 150 <= elapsed <= 152 and not ambulance_2_sent:
        ambulance_event = generate_ambulance_event("1", "Emergencia médica - Ambulancia 2")
        socket.send_string("ambulancia " + json.dumps(ambulance_event))
        timestamp_legible = ambulance_event.get("timestamp_legible", "N/A")
        sensor_id = ambulance_event.get("sensor_id", "N/A")
        fila = ambulance_event.get("fila", "N/A")
        motivo = ambulance_event.get("motivo", "N/A")
        intersecciones = ", ".join(ambulance_event.get("intersecciones", []))
        print(f"\n[{timestamp_legible}] [AMBULANCIA] {sensor_id} - Fila: {fila}, Motivo: {motivo}")
        print(f"[{timestamp_legible}]              Intersecciones: {intersecciones}\n")
        ambulance_2_sent = True
    
    time.sleep(SENSOR_INTERVAL)

