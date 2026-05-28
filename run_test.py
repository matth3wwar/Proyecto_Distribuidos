#!/usr/bin/env python3
"""
run_test.py - Script para ejecutar el sistema de prueba completo
Ejecutar con: python run_test.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_header(text, color="cyan"):
    """Imprime un encabezado con color"""
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"\n{colors.get(color, '')}{text}{colors['reset']}")

def start_process(directory, command, title):
    """Inicia un nuevo proceso en una terminal separada"""
    try:
        full_command = f'powershell -NoExit -Command "cd \'{directory}\'; {command}"'
        subprocess.Popen(
            ["powershell", "-NoExit", "-Command", f"cd '{directory}'; {command}"],
            cwd=directory
        )
    except Exception as e:
        print(f"Error al iniciar {title}: {e}")

def main():
    print_header("=" * 50, "cyan")
    print_header("SISTEMA DE PRUEBA - TRÁFICO CON ZEROMQ", "cyan")
    print_header("=" * 50, "cyan")
    
    workspace = Path(__file__).parent.absolute()
    
    print(f"\nDirectorio raíz: {workspace}")
    print("\nServicios a iniciar:")
    print("1. PC1: Broker ZMQ")
    print("2. PC2: Control de semáforos")
    print("3. PC2: Base de datos réplica")
    print("4. PC3: Base de datos principal")
    print("5. PC2: Servicio de analítica")
    print("6. PC3: Módulo de consultas")
    print("7. ROOT: Sensores (ÚLTIMA - inicia la simulación)")
    
    input("\nPresiona Enter para comenzar...")
    
    print_header("Iniciando servicios...", "green")
    
    services = [
        ("PC_1", "python broker_mq.py", "PC1 - Broker ZMQ"),
        ("PC_2", "python control_semaforos.py", "PC2 - Control de semáforos"),
        ("PC_2", "python db_replica.py", "PC2 - BD Réplica"),
        ("PC_3", "python db.py", "PC3 - BD Principal"),
        ("PC_2", "python analisis.py", "PC2 - Servicio de analítica"),
        ("PC_3", "python consultas.py", "PC3 - Módulo de consultas"),
    ]
    
    for i, (subdir, command, title) in enumerate(services, 1):
        directory = str(workspace / subdir)
        print(f"\n[{i}/6] Iniciando {title}...")
        start_process(directory, command, title)
        time.sleep(2)
    
    # Iniciar sensores (última)
    print(f"\n[7/7] Iniciando Sensores (¡SIMULACIÓN COMIENZA!)...")
    start_process(str(workspace), "python sensores.py", "SENSORES")
    
    print_header("✓ Todos los servicios iniciados", "green")
    print("\nCronograma de eventos:")
    print("  60s  → Congestión en INT_2b")
    print("  95s  → Congestión en INT_3d")
    print("  130s → Ambulancia 1 en Fila 1")
    print("  140s → Fallo de BD Principal (PC3)")
    print("  150s → Ambulancia 2 en Fila 1")
    
    print_header("Observa los logs en cada terminal para ver los eventos en tiempo real.", "cyan")

if __name__ == "__main__":
    main()
