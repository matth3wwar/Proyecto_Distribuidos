import zmq

context = zmq.Context()

sensores = context.socket(zmq.SUB)
sensores.bind("tcp://*:5556")
sensores.setsockopt_string(zmq.SUBSCRIBE, "")

backend = context.socket(zmq.PUB)
backend.bind("tcp://*:5557")

print("Broker activo...")

while True:

    message = sensores.recv()
    backend.send(message)
    print("Broker envía: ", message)