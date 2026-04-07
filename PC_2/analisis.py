import zmq
import json

context = zmq.Context()

# Recibe datos
sub_socket = context.socket(zmq.SUB)
sub_socket.connect("tcp://localhost:5557")
sub_socket.setsockopt_string(zmq.SUBSCRIBE, "traffic")

# Enviar a BD
push_db = context.socket(zmq.PUSH)
push_db.connect("tcp://localhost:5558")

# Enviar a semáforos
push_traffic = context.socket(zmq.PUSH)
push_traffic.connect("tcp://localhost:5559")

print("Servicio de analítica activo...")

def evaluar(evento):
    if evento["tipo"] == "camara":
        if evento["volumen"] > 5:
            return "CONGESTION"
    return "NORMAL"

while True:
    msg = sub_socket.recv_string()
    _, data = msg.split(" ", 1)
    evento = json.loads(data)

    estado = evaluar(evento)
    evento["estado"] = estado

    print("Analítica procesó:", evento)

    push_db.send_json(evento)

    if estado == "CONGESTION":
        push_traffic.send_json({
            "accion": "EXTENDER_VERDE",
            "interseccion": evento["interseccion"]
        })