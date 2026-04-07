# pc1/sensors.py
import zmq
import time
import json
import random
from config import BROKER_SUB_ADDRESS

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.connect(BROKER_SUB_ADDRESS)

def generate_camera_event():
    return {
        "tipo": "camara",
        "interseccion": "INT-C5",
        "volumen": random.randint(0, 15),
        "velocidad_promedio": random.randint(10, 50),
        "timestamp": time.time()
    }

def generate_espira_event():
    return {
        "tipo": "espira",
        "interseccion": "INT-C5",
        "vehiculos": random.randint(5, 20),
        "timestamp": time.time()
    }

def generate_gps_event():
    return {
        "tipo": "gps",
        "interseccion": "INT-C5",
        "velocidad_promedio": random.randint(5, 50),
        "timestamp": time.time()
    }

while True:
    event = random.choice([
        generate_camera_event(),
        generate_espira_event(),
        generate_gps_event()
    ])
    
    socket.send_string("traffic " + json.dumps(event))
    print("Sensor envió:", event)
    time.sleep(2)