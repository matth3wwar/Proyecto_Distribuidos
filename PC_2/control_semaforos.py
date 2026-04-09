#######################################################################################
#
#
###################################################################################
# control_semaforos.py
import zmq
from config import TRAFFIC_BIND_ADDRESS, NORMAL_GREEN_TIME

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(TRAFFIC_BIND_ADDRESS)

print("Control de semáforos activo...")

estados = {}

while True:
    comando = socket.recv_json()

    interseccion = comando["interseccion"]
    accion = comando["accion"]

    if accion == "EXTENDER_VERDE":
        estados[interseccion] = "VERDE_EXTENDIDO"
        print(f"Semáforo {interseccion}: VERDE_EXTENDIDO ({NORMAL_GREEN_TIME}s + extra)")
    elif accion == "CAMBIAR_A_VERDE":
        estados[interseccion] = "VERDE"
        print(f"Semáforo {interseccion}: VERDE")
    else:
        estados[interseccion] = "ROJO"
        print(f"Semáforo {interseccion}: ROJO")

    print("Comando recibido:", comando)