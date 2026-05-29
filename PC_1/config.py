##############################################################################
#   config.py
############################################################################

#info adress

PC1_IP = "192.168.11.13"
PC2_IP = "192.168.11.15"
PC3_IP = "192.168.11.13"

BROKER_SUB_ADDRESS = "tcp://*:5556"
BROKER_PUB_ADDRESS = "tcp://*:5557"

ANALYTICS_SUB_ADDRESS = f"tcp://{PC1_IP}:5557"
DB_PUSH_ADDRESS = f"tcp://{PC2_IP}:5558"
DB_REPLICA_PUSH_ADDRESS = f"tcp://{PC2_IP}:5560"
TRAFFIC_PUSH_ADDRESS = f"tcp://{PC2_IP}:5559"
QUERY_PULL_ADDRESS = f"tcp://{PC2_IP}:5561"

DB_BIND_ADDRESS = "tcp://*:5558"
DB_REPLICA_BIND_ADDRESS = "tcp://*:5560"
TRAFFIC_BIND_ADDRESS = "tcp://*:5559"
QUERY_BIND_ADDRESS = "tcp://*:5561"

#Info simulacion ciudad - Matriz 3x5
# Filas: 1, 2, 3
# Columnas: a, b, c, d, e

INTERSECCIONES = [
    "INT_1a", "INT_1b", "INT_1c", "INT_1d", "INT_1e",  # Fila 1
    "INT_2a", "INT_2b", "INT_2c", "INT_2d", "INT_2e",  # Fila 2
    "INT_3a", "INT_3b", "INT_3c", "INT_3d", "INT_3e"   # Fila 3
]

SENSOR_INTERVAL = 2

NORMAL_GREEN_TIME = 15
DB_FAILURE_TIME = 140  # segundos