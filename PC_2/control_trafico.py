import zmq
from PC_1.config import DEFAULT_GREEN_TIME

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5559")

# Estado por intersección
semaforos = {}

print("Control de semáforos activo...")

while True:
    msg = socket.recv_json()

    inter = msg["interseccion"]
    estado = msg["estado"]
    tiempo = msg["tiempo_verde"]

    semaforos[inter] = {
        "estado": estado,
        "tiempo_verde": tiempo
    }

    print(f"[{inter}] -> {estado} | Verde: {tiempo}s")