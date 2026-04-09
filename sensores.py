##############################################################################
#
#
################################################################################
# sensores.py
import zmq
import time
import json
import random
from config import BROKER_SUB_ADDRESS, INTERSECCIONES, SENSOR_INTERVAL

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(BROKER_SUB_ADDRESS)

def generate_camera_event(interseccion):
    return {
        "sensor_id": f"CAM-{interseccion}",
        "tipo_sensor": "camara",
        "interseccion": interseccion,
        "volumen": random.randint(0, 15),
        "velocidad_promedio": random.randint(10, 50),
        "timestamp": time.time()
    }

def generate_espira_event(interseccion):
    inicio = time.time()
    return {
        "sensor_id": f"ESP-{interseccion}",
        "tipo_sensor": "espira_inductiva",
        "interseccion": interseccion,
        "vehiculos_contados": random.randint(5, 20),
        "intervalo_segundos": 30,
        "timestamp_inicio": inicio,
        "timestamp_fin": inicio + 30
    }

def generate_gps_event(interseccion):
    velocidad = random.randint(5, 50)

    if velocidad < 10:
        nivel = "BAJA"
    elif velocidad <= 39:
        nivel = "NORMAL"
    else:
        nivel = "ALTA"

    return {
        "sensor_id": f"GPS-{interseccion}",
        "tipo_sensor": "gps",
        "interseccion": interseccion,
        "nivel_congestion": nivel,
        "velocidad_promedio": velocidad,
        "timestamp": time.time()
    }

while True:
    interseccion = random.choice(INTERSECCIONES)
    tipo = random.choice(["camara", "espira", "gps"])

    if tipo == "camara":
        event = generate_camera_event(interseccion)
        topic = "camara"
    elif tipo == "espira":
        event = generate_espira_event(interseccion)
        topic = "espira"
    else:
        event = generate_gps_event(interseccion)
        topic = "gps"

    socket.send_string(topic + " " + json.dumps(event))
    print("Sensor envió:", topic, event)
    time.sleep(SENSOR_INTERVAL)
