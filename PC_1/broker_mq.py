###############################################################################
#
#
##############################################################################
# broker_mq.py
import zmq

context = zmq.Context()

from config import BROKER_SUB_ADDRESS, BROKER_PUB_ADDRESS

frontend = context.socket(zmq.SUB)
frontend.bind(BROKER_SUB_ADDRESS)
frontend.setsockopt_string(zmq.SUBSCRIBE, "camara")
frontend.setsockopt_string(zmq.SUBSCRIBE, "espira")
frontend.setsockopt_string(zmq.SUBSCRIBE, "gps")

backend = context.socket(zmq.PUB)
backend.bind(BROKER_PUB_ADDRESS)

print("Broker activo...")

while True:
    message = frontend.recv()
    print("Broker recibio:", message.decode())
    backend.send(message)
