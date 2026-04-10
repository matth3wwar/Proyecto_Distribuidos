# db.py
import zmq
import json
from config import DB_PUSH_ADDRESS

context = zmq.Context()

socket = context.socket(zmq.PULL)
socket.bind(DB_PUSH_ADDRESS)

print("Base de datos activa...")

while True:
    data = socket.recv_json()
    print("Guardando en BD:", data)

    with open("db.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")