##############################################################################
#   config.py
#
##############################################################################
PC1_IP = "127.0.0.1"
PC2_IP = "127.0.0.2"
PC3_IP = "127.0.0.1"



BROKER_SUB_ADDRESS = "tcp://{PC1_IP}:5556"
BROKER_PUB_ADDRESS = "tcp://*:5557"

ANALYTICS_SUB_ADDRESS = "tcp://{PC1_IP}:5557"
DB_PUSH_ADDRESS = "tcp://{PC3_IP}:5558"
TRAFFIC_PUSH_ADDRESS = "tcp://{PC2_IP}:5559"

DB_BIND_ADDRESS = f"tcp://*:5558"
TRAFFIC_BIND_ADDRESS = f"tcp://*:5559"

# =========================
# Ciudad simple
# =========================
INTERSECCIONES = ["INT_A1", "INT_A2", "INT_B1", "INT_B2"]