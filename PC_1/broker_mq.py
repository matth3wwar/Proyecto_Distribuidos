###############################################################################
#
# broker_mq.py - Broker ZeroMQ
##############################################################################
import zmq

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
    print("[BROKER] Retransmitiendo:", message.decode()[:100] + "...")
    backend.send(message)

