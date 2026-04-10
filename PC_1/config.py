##############################################################################
#   config.py
############################################################################

#info adress

PC1_IP = "192.168.11.10"
PC2_IP = "192.168.11.15"
PC3_IP = "192.168.11.10"

BROKER_SUB_ADDRESS = "tcp://*:5556"
BROKER_PUB_ADDRESS = "tcp://*:5557"

ANALYTICS_SUB_ADDRESS = f"tcp://{PC1_IP}:5557"
DB_PUSH_ADDRESS = f"tcp://{PC2_IP}:5558"
DB_REPLICA_PUSH_ADDRESS = f"tcp://{PC2_IP}:5560"
TRAFFIC_PUSH_ADDRESS = f"tcp://{PC2_IP}:5559"

DB_BIND_ADDRESS = "tcp://*:5558"
DB_REPLICA_BIND_ADDRESS = "tcp://*:5560"
TRAFFIC_BIND_ADDRESS = "tcp://*:5559"

#Info simulacion ciudad

INTERSECCIONES = ["INT_A1", "INT_A2", "INT_B1", "INT_B2"]

SENSOR_INTERVAL = 2

NORMAL_GREEN_TIME = 15