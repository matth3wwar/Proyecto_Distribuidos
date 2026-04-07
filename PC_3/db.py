import zmq
import json

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5558")

print("Base de datos activa...")

while True:
    data = socket.recv_json()
    print("Guardando en BD:", data)

    with open("db.json", "a") as f:
        f.write(json.dumps(data) + "\n")