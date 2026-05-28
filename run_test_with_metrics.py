# run_test_with_metrics.py - Ejecuta la prueba completa y genera métricas de desempeño
import subprocess
import time
import os
import sys
from pathlib import Path
from metrics import generate_metrics_report

def print_header(text, color="cyan"):
    """Imprime encabezado formateado"""
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"\n{colors.get(color, '')}{text}{colors['reset']}")

def start_service(directory, command, service_name):
    """Inicia un servicio en terminal separada"""
    try:
        if sys.platform == "win32":
            # Windows: Abrir en nueva ventana PowerShell
            full_command = f"cd '{directory}' && {command}"
            subprocess.Popen(
                ["powershell", "-NoExit", "-Command", full_command],
                cwd=directory
            )
        else:
            # Linux/Mac
            subprocess.Popen(
                ["gnome-terminal", "--", "bash", "-c", f"cd {directory} && {command} && read"],
                cwd=directory
            )
        print(f"  [OK] {service_name} iniciado")
    except Exception as e:
        print(f"  [ERROR] {service_name}: {e}")

def cleanup_old_data():
    """Limpia archivos de datos antiguos"""
    print_header("[SETUP] Limpiando datos anteriores...", "yellow")
    
    files_to_remove = [
        "PC_3/db.json",
        "PC_2/db_replica.json",
        "events_trace.jsonl",
        "METRICS_REPORT.md"
    ]
    
    for filepath in files_to_remove:
        if Path(filepath).exists():
            try:
                Path(filepath).unlink()
                print(f"  [OK] Removido: {filepath}")
            except Exception as e:
                print(f"  [WARNING] No se pudo remover {filepath}: {e}")

def wait_for_completion(duration_seconds=185, check_interval=5):
    """Espera a que la prueba se complete"""
    print_header(f"[RUNNING] Prueba en ejecución por {duration_seconds} segundos...", "green")
    
    start = time.time()
    
    while time.time() - start < duration_seconds:
        remaining = int(duration_seconds - (time.time() - start))
        key_times = [60, 95, 130, 140, 150]
        
        current = int(time.time() - start)
        
        for key_time in key_times:
            if current == key_time:
                if key_time == 60:
                    print_header(f">>> EVENTO: Congestión esperada en INT_2b <<<", "blue")
                elif key_time == 95:
                    print_header(f">>> EVENTO: Congestión esperada en INT_3d <<<", "blue")
                elif key_time == 130:
                    print_header(f">>> EVENTO: Ambulancia 1 esperada <<<", "blue")
                elif key_time == 140:
                    print_header(f">>> EVENTO: Fallo de BD Principal esperado <<<", "red")
                elif key_time == 150:
                    print_header(f">>> EVENTO: Ambulancia 2 esperada <<<", "blue")
        
        print(f"\r  Tiempo transcurrido: {current}s / {duration_seconds}s ({remaining}s restantes)", end="", flush=True)
        time.sleep(check_interval)
    
    print(f"\r  Tiempo transcurrido: {duration_seconds}s / {duration_seconds}s - COMPLETADO      \n")

def collect_metrics():
    """Recopila y genera reporte de métricas"""
    print_header("RECOPILANDO MÉTRICAS DE DESEMPEÑO", "green")
    
    # Dar tiempo a los archivos para sincronizarse
    time.sleep(2)
    
    # Generar reporte
    resultado = generate_metrics_report()
    
    return resultado

def main():
    """Ejecuta el flujo completo de prueba con métricas"""
    
    print_header("="*80, "cyan")
    print_header("SISTEMA DE PRUEBA CON MÉTRICAS DE DESEMPEÑO", "cyan")
    print_header("="*80, "cyan")
    
    # 1. Limpiar datos anteriores
    cleanup_old_data()
    
    # 2. Confirmación del usuario
    print_header("\nConfiguración lista. Presiona Enter para comenzar la prueba...", "yellow")
    input()
    
    # 3. Iniciar servicios
    print_header("INICIANDO SERVICIOS", "green")
    
    workspace = Path(__file__).parent.absolute()
    
    servicios = [
        ("PC_1", "python broker_mq.py", "[1/7] PC1: Broker ZMQ"),
        ("PC_2", "python control_semaforos.py", "[2/7] PC2: Control Semáforos"),
        ("PC_2", "python db_replica.py", "[3/7] PC2: BD Réplica"),
        ("PC_3", "python db.py", "[4/7] PC3: BD Principal"),
        ("PC_2", "python analisis.py", "[5/7] PC2: Analítica"),
        ("PC_3", "python consultas.py", "[6/7] PC3: Consultas"),
    ]
    
    for subdir, command, nombre in servicios:
        directory = str(workspace / subdir)
        start_service(directory, command, nombre)
        time.sleep(1.5)
    
    # 4. Iniciar sensores (último - inicia el cronograma)
    print_header("INICIANDO SENSORES (Comienza el cronograma)", "green")
    start_service(str(workspace), "python sensores.py", "[7/7] SENSORES")
    
    # 5. Esperar a que se complete
    time.sleep(2)  # Dar tiempo a sensores para inicializar
    wait_for_completion(duration_seconds=185)
    
    # 6. Recopilar métricas
    time.sleep(3)
    resultado = collect_metrics()
    
    # 7. Resumen final
    print_header("RESUMEN FINAL", "green")
    print(f"  BD Principal: {resultado['db_principal']['eventos_totales']} eventos")
    print(f"  BD Réplica: {resultado['db_replica']['eventos_totales']} eventos")
    print(f"  Reporte guardado: {resultado['reporte']}")
    
    print_header("PRUEBA COMPLETADA EXITOSAMENTE", "green")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_header("\nPrueba interrumpida por el usuario", "yellow")
        sys.exit(0)
    except Exception as e:
        print_header(f"Error: {e}", "red")
        sys.exit(1)
