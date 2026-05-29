# pc1/sensors.py
import zmq
import time
import json
import random
from config import BROKER_SUB_ADDRESS, GRID_ROWS, GRID_COLS

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(BROKER_SUB_ADDRESS)
timestamp_unix = time.time()
congestion_b2_sent = False
congestion_3e_sent = False

def generar_intersecciones():
    return [f"INT-{r}{c}" for r in GRID_ROWS for c in GRID_COLS]

INTERSECCIONES = generar_intersecciones()

def generate_camera_event(inter):
    return {
        "tipo": "camara",
        "interseccion": inter,
        "volumen": random.randint(0, 15),
        "timestamp": time.time()
    }

def generate_congestion_camera_event(inter):
    return {
        "tipo": "congestion_camara",
        "interseccion": inter,
        "volumen": 20,
        "timestamp": time.time()
    }

def generate_espira_event(inter):
    return {
        "tipo": "espira",
        "interseccion": inter,
        "vehiculos": random.randint(5, 20),
        "timestamp": time.time()
    }

def generate_gps_event(inter):
    return {
        "tipo": "gps",
        "interseccion": inter,
        "volumen": random.randint(0, 15),
        "velocidad_promedio": random.randint(10, 50),
        "timestamp": time.time()
    }

while True:
    if timestamp_unix >=60 and not congestion_b2_sent:
        generate_congestion_camera_event("INT_2b")
        congestion_b2_sent = True
    if timestamp_unix >=95 and not congestion_3e_sent:
        generate_congestion_camera_event("INT_3e")
        congestion_3e_sent = True
    for inter in INTERSECCIONES:
        evento = generate_camera_event(inter)
        socket.send_string("traffic " + json.dumps(evento))
        print("Sensor envió:", evento)

        evento = generate_espira_event(inter)
        socket.send_string("traffic " + json.dumps(evento))
        print("Sensor envió:", evento)

        evento = generate_gps_event(inter)
        socket.send_string("traffic " + json.dumps(evento))
        print("Sensor envió:", evento)
    
    time.sleep(3)