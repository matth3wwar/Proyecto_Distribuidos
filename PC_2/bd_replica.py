import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:5560")

print("[Servicio de Base de Datos Réplica]")

while True:
    data = socket.recv_json()

    with open("db_replica.json", "a") as f:
        f.write(json.dumps(data) + "\n")

    print("BD Réplica guardó:", data)