###############################################################################
#
# broker_mq.py - Broker ZeroMQ
##############################################################################
import zmq
import json

context = zmq.Context()
from config import BROKER_SUB_ADDRESS, BROKER_PUB_ADDRESS

frontend = context.socket(zmq.SUB)
frontend.bind(BROKER_SUB_ADDRESS)
frontend.setsockopt_string(zmq.SUBSCRIBE, "camara")
frontend.setsockopt_string(zmq.SUBSCRIBE, "espira")
frontend.setsockopt_string(zmq.SUBSCRIBE, "gps")
frontend.setsockopt_string(zmq.SUBSCRIBE, "ambulancia")

backend = context.socket(zmq.PUB)
backend.bind(BROKER_PUB_ADDRESS)

print("[BROKER] Broker ZMQ activo...")
print("[BROKER] Canales activos: camara, espira, gps, ambulancia\n")

while True:
    message = frontend.recv()
    message_decoded = message.decode()
    
    # Extraer tipo de sensor y datos JSON
    try:
        partes = message_decoded.split(" ", 1)
        if len(partes) == 2:
            tipo_sensor, json_str = partes
            evento = json.loads(json_str)
            timestamp_legible = evento.get("timestamp_legible", "N/A")
            interseccion = evento.get("interseccion", "N/A")
            sensor_id = evento.get("sensor_id", "N/A")
            
            # Mostrar información completa y legible
            print(f"[BROKER] [{timestamp_legible}] Retransmitiendo {tipo_sensor.upper()} - {sensor_id} en {interseccion}")
        else:
            print(f"[BROKER] Retransmitiendo: {message_decoded}")
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"[BROKER] Retransmitiendo: {message_decoded[:100]}...")
    
    backend.send(message)

