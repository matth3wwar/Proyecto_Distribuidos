##############################################################################
#
#
##############################################################################
# analisis.py
import zmq
import json
from config import ANALYTICS_SUB_ADDRESS, DB_PUSH_ADDRESS, DB_REPLICA_PUSH_ADDRESS, TRAFFIC_PUSH_ADDRESS

context = zmq.Context()

# broker
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(ANALYTICS_SUB_ADDRESS)
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "camara")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "espira")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "gps")

# BD principal
push_db = context.socket(zmq.PUSH)
push_db.connect(DB_PUSH_ADDRESS)

# BD replica
push_db_r = context.socket(zmq.PUSH)
push_db_r.connect(DB_REPLICA_PUSH_ADDRESS)


# Control de semáforos
push_traffic = context.socket(zmq.PUSH)
push_traffic.connect(TRAFFIC_PUSH_ADDRESS)

print("Servicio de analítica activo...")

def evaluar(topic, evento):
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

while True:
    msg = sub_socket.recv_string()
    topic, data = msg.split(" ", 1)
    evento = json.loads(data)

    estado = evaluar(topic, evento)
    evento["estado"] = estado
    evento["topic"] = topic

    print("Analítica procesó:", evento)

    # guardar en BD's
    push_db.send_json(evento)
    push_db_r.send_json(evento)

    # tomar decisión sobre semáforo
    if estado == "CONGESTION":
        push_traffic.send_json({
            "accion": "EXTENDER_VERDE",
            "interseccion": evento["interseccion"],
            "motivo": f"Congestión detectada por {topic}"
        })
