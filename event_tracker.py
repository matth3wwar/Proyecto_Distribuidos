# event_tracker.py - Rastreador centralizado de eventos con timestamps precisos
import json
import time
from threading import Lock
from pathlib import Path

class EventTracker:
    """Rastrea eventos con timestamps precisos para análisis de desempeño"""
    
    def __init__(self, log_file="events_trace.jsonl"):
        self.log_file = log_file
        self.lock = Lock()
        self.start_time = time.time()
        self.event_count = 0
        
        # Limpiar archivo anterior
        if Path(log_file).exists():
            Path(log_file).unlink()
    
    def get_elapsed(self):
        """Obtiene tiempo transcurrido desde inicio"""
        return time.time() - self.start_time
    
    def log_event(self, event_type, component, interseccion=None, details=None):
        """
        Registra un evento con timestamp preciso
        
        Args:
            event_type: Tipo de evento (SENSOR, DETECTION, COMMAND, DB_FAILURE, etc)
            component: Componente que genera el evento
            interseccion: Intersección afectada (opcional)
            details: Detalles adicionales (dict)
        """
        elapsed = self.get_elapsed()
        
        event = {
            "timestamp": time.time(),
            "elapsed_seconds": elapsed,
            "event_type": event_type,
            "component": component,
            "interseccion": interseccion,
            "details": details or {},
        }
        
        with self.lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(event) + "\n")
                self.event_count += 1
            except Exception as e:
                print(f"[ERROR] EventTracker: No se pudo escribir evento: {e}")
    
    def analyze_latencies(self, event_types_pair=("DETECTION", "COMMAND")):
        """
        Analiza latencias entre dos tipos de eventos
        
        Args:
            event_types_pair: Tuple (evento_origen, evento_destino)
        
        Returns:
            dict con estadísticas de latencia
        """
        if not Path(self.log_file).exists():
            return {"error": "No events logged"}
        
        detections = []
        commands = []
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for linea in f:
                    evento = json.loads(linea)
                    
                    if evento['event_type'] == event_types_pair[0]:
                        detections.append((evento['elapsed_seconds'], evento.get('interseccion')))
                    elif evento['event_type'] == event_types_pair[1]:
                        commands.append((evento['elapsed_seconds'], evento.get('interseccion')))
        
        except Exception as e:
            return {"error": f"Error reading events: {e}"}
        
        # Calcular latencias por intersección
        latencies_by_intersection = {}
        
        for det_time, det_int in detections:
            if det_int not in latencies_by_intersection:
                latencies_by_intersection[det_int] = []
            
            # Buscar primer comando posterior
            for cmd_time, cmd_int in commands:
                if cmd_int == det_int and cmd_time >= det_time:
                    latency_ms = (cmd_time - det_time) * 1000
                    latencies_by_intersection[det_int].append(latency_ms)
                    break
        
        # Calcular estadísticas
        stats = {}
        for interseccion, latencies in latencies_by_intersection.items():
            if latencies:
                stats[interseccion] = {
                    "count": len(latencies),
                    "avg_ms": sum(latencies) / len(latencies),
                    "min_ms": min(latencies),
                    "max_ms": max(latencies),
                }
        
        return stats
    
    def get_report(self):
        """Obtiene reporte resumido de eventos"""
        if not Path(self.log_file).exists():
            return {}
        
        stats = {
            "total_events": 0,
            "by_type": {},
            "by_component": {},
        }
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for linea in f:
                    evento = json.loads(linea)
                    
                    stats["total_events"] += 1
                    
                    event_type = evento.get('event_type', 'UNKNOWN')
                    stats["by_type"][event_type] = stats["by_type"].get(event_type, 0) + 1
                    
                    component = evento.get('component', 'UNKNOWN')
                    stats["by_component"][component] = stats["by_component"].get(component, 0) + 1
        
        except Exception as e:
            return {"error": str(e)}
        
        return stats

# Instancia global
event_tracker = EventTracker("events_trace.jsonl")

if __name__ == "__main__":
    # Test
    print("[EVENT_TRACKER] Iniciando prueba...")
    
    event_tracker.log_event("SENSOR", "SENSORES", "INT_2b", {"tipo_sensor": "camara"})
    time.sleep(0.1)
    event_tracker.log_event("DETECTION", "ANALÍTICA", "INT_2b", {"motivo": "congestion"})
    time.sleep(0.05)
    event_tracker.log_event("COMMAND", "SEMÁFOROS", "INT_2b", {"accion": "VERDE_EXTENDIDO"})
    
    print("[EVENT_TRACKER] Eventos registrados")
    print(event_tracker.get_report())
    print("[EVENT_TRACKER] Análisis de latencias:")
    print(event_tracker.analyze_latencies(("DETECTION", "COMMAND")))
