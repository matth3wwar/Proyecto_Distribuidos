###############################################################################
#
#
##############################################################################
# broker_mq.py
import zmq

context = zmq.Context()

frontend = context.socket(zmq.SUB)
frontend.bind("tcp://*:5556")
frontend.setsockopt_string(zmq.SUBSCRIBE, "camara")
frontend.setsockopt_string(zmq.SUBSCRIBE, "espira")
frontend.setsockopt_string(zmq.SUBSCRIBE, "gps")

backend = context.socket(zmq.PUB)
backend.bind("tcp://*:5557")

print("Broker activo...")

while True:
    message = frontend.recv()
    print("Broker recibió:", message.decode())
    backend.send(message)
