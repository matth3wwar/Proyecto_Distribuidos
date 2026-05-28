# analyze_logs.py - Analiza logs de servicios para extraer métricas
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict, Any

class LogAnalyzer:
    """Analiza logs de consola de servicios para extraer métricas de desempeño"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
        self.events = []
        self.congestion_detections = []
        self.semaforo_commands = []
        self.ambulance_events = []
        self.db_failures = []
    
    def parse_log_line(self, line: str) -> Dict[str, Any]:
        """
        Parsea una línea de log y extrae información
        
        Formatos esperados:
        [60.1s] [ANALÍTICA] CONGESTION detectada en INT_2b
        [60.1s] [SEMÁFOROS] Comando para INT_2b
        [130.2s] AMBULANCIA SOLICITANDO PASO en Fila 1
        """
        result = {}
        
        # Extraer timestamp
        time_match = re.match(r'\[(\d+\.\d+)s\]', line)
        if time_match:
            result['elapsed'] = float(time_match.group(1))
        
        # Extraer componente
        if '[ANALÍTICA]' in line:
            result['component'] = 'ANALÍTICA'
        elif '[SEMÁFOROS]' in line:
            result['component'] = 'SEMÁFOROS'
        elif '[DB' in line:
            result['component'] = 'DATABASE'
        elif '[CONSULTAS]' in line:
            result['component'] = 'CONSULTAS'
        else:
            result['component'] = 'OTHER'
        
        result['raw'] = line
        return result
    
    def extract_congestion_detections(self, log_content: str) -> List[Tuple[float, str]]:
        """
        Extrae detecciones de congestión del log de analítica
        
        Returns:
            Lista de tuples (tiempo_segundos, interseccion)
        """
        detections = []
        
        # Buscar líneas con CONGESTION
        pattern = r'\[(\d+\.\d+)s\].*CONGESTION.*?INT_(\w+)'
        matches = re.findall(pattern, log_content, re.IGNORECASE)
        
        for match in matches:
            tiempo = float(match[0])
            interseccion = f"INT_{match[1]}"
            detections.append((tiempo, interseccion))
        
        return detections
    
    def extract_semaforo_commands(self, log_content: str) -> List[Tuple[float, str, str]]:
        """
        Extrae comandos de semáforo ejecutados
        
        Returns:
            Lista de tuples (tiempo_segundos, interseccion, accion)
        """
        commands = []
        
        # Buscar líneas con estado de semáforo
        patterns = [
            (r'\[(\d+\.\d+)s\].*INT_(\w+).*VERDE PRIORITARIO', 'VERDE_AMBULANCIA'),
            (r'\[(\d+\.\d+)s\].*INT_(\w+).*VERDE_EXTENDIDO', 'VERDE_EXTENDIDO'),
            (r'\[(\d+\.\d+)s\].*INT_(\w+).*\[OK\] Estado: VERDE(?!_)', 'VERDE'),
        ]
        
        for pattern, accion in patterns:
            matches = re.findall(pattern, log_content, re.IGNORECASE)
            for match in matches:
                tiempo = float(match[0])
                interseccion = f"INT_{match[1]}"
                commands.append((tiempo, interseccion, accion))
        
        return commands
    
    def extract_ambulance_events(self, log_content: str) -> List[Tuple[float, int]]:
        """
        Extrae eventos de ambulancia
        
        Returns:
            Lista de tuples (tiempo_segundos, fila)
        """
        events = []
        
        pattern = r'\[(\d+\.\d+)s\].*AMBULANCIA.*Fila (\d)'
        matches = re.findall(pattern, log_content, re.IGNORECASE)
        
        for match in matches:
            tiempo = float(match[0])
            fila = int(match[1])
            events.append((tiempo, fila))
        
        return events
    
    def extract_db_failures(self, log_content: str) -> List[float]:
        """
        Extrae tiempos de fallo de BD
        
        Returns:
            Lista de tiempos de fallo
        """
        failures = []
        
        pattern = r'\[(\d+\.\d+)s\].*FALLO.*BD.*PRINCIPAL'
        matches = re.findall(pattern, log_content, re.IGNORECASE)
        
        for match in matches:
            failures.append(float(match))
        
        return failures
    
    def calculate_reaction_times(self) -> Dict[str, Any]:
        """
        Calcula tiempos de reacción DETECTION -> COMMAND
        
        Returns:
            Estadísticas de latencia por intersección
        """
        latencies_by_intersection = defaultdict(list)
        
        # Agrupar por intersección
        for det_time, det_int in self.congestion_detections:
            for cmd_time, cmd_int, cmd_action in self.semaforo_commands:
                if det_int == cmd_int and cmd_time >= det_time:
                    latency_ms = (cmd_time - det_time) * 1000
                    latencies_by_intersection[det_int].append({
                        'latency_ms': latency_ms,
                        'detection_time': det_time,
                        'command_time': cmd_time,
                        'action': cmd_action
                    })
                    break
        
        # Calcular estadísticas
        stats = {}
        for intersection, latencies in latencies_by_intersection.items():
            if latencies:
                values = [l['latency_ms'] for l in latencies]
                stats[intersection] = {
                    'count': len(latencies),
                    'avg_ms': sum(values) / len(values),
                    'min_ms': min(values),
                    'max_ms': max(values),
                    'events': latencies
                }
        
        return stats
    
    def generate_report(self, output_file="LOG_ANALYSIS_REPORT.md") -> str:
        """Genera reporte de análisis de logs"""
        report = []
        report.append("# Análisis de Logs de Desempeño\n\n")
        
        # Detecciones de congestión
        report.append("## Detecciones de Congestión\n\n")
        report.append("| Tiempo (s) | Intersección |\n")
        report.append("|---|---|\n")
        for tiempo, interseccion in sorted(self.congestion_detections):
            report.append(f"| {tiempo:.2f} | {interseccion} |\n")
        report.append(f"\n**Total**: {len(self.congestion_detections)} detecciones\n\n")
        
        # Comandos de semáforo
        report.append("## Comandos de Semáforo Ejecutados\n\n")
        report.append("| Tiempo (s) | Intersección | Acción |\n")
        report.append("|---|---|---|\n")
        for tiempo, interseccion, accion in sorted(self.semaforo_commands):
            report.append(f"| {tiempo:.2f} | {interseccion} | {accion} |\n")
        report.append(f"\n**Total**: {len(self.semaforo_commands)} comandos\n\n")
        
        # Eventos de ambulancia
        report.append("## Eventos de Ambulancia\n\n")
        report.append("| Tiempo (s) | Fila |\n")
        report.append("|---|---|\n")
        for tiempo, fila in sorted(self.ambulance_events):
            report.append(f"| {tiempo:.2f} | {fila} |\n")
        report.append(f"\n**Total**: {len(self.ambulance_events)} ambulancias\n\n")
        
        # Tiempos de reacción
        reaction_times = self.calculate_reaction_times()
        report.append("## Tiempos de Reacción (Detección → Comando)\n\n")
        report.append("| Intersección | Count | Promedio (ms) | Mín (ms) | Máx (ms) |\n")
        report.append("|---|---|---|---|---|\n")
        
        for intersection in sorted(reaction_times.keys()):
            stats = reaction_times[intersection]
            report.append(f"| {intersection} | {stats['count']} | {stats['avg_ms']:.2f} | {stats['min_ms']:.2f} | {stats['max_ms']:.2f} |\n")
        
        if reaction_times:
            all_latencies = []
            for stats in reaction_times.values():
                all_latencies.extend([e['latency_ms'] for e in stats['events']])
            
            report.append(f"\n**Promedio Global**: {sum(all_latencies) / len(all_latencies):.2f} ms\n")
            report.append(f"**Mínimo**: {min(all_latencies):.2f} ms\n")
            report.append(f"**Máximo**: {max(all_latencies):.2f} ms\n\n")
        
        # Fallos de BD
        if self.db_failures:
            report.append("## Fallos de Base de Datos\n\n")
            report.append("| Tiempo (s) | Evento |\n")
            report.append("|---|---|\n")
            for failure_time in self.db_failures:
                report.append(f"| {failure_time:.2f} | BD Principal falló - Fallover a Réplica |\n")
            report.append("\n")
        
        report_text = "".join(report)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text

# Funciones helper
def analyze_trace_file(trace_file="events_trace.jsonl") -> Dict[str, Any]:
    """Analiza archivo de trazas de eventos"""
    if not Path(trace_file).exists():
        return {"error": "Trace file not found"}
    
    stats = {
        "total_events": 0,
        "by_type": defaultdict(int),
        "by_component": defaultdict(int),
        "detections": [],
        "commands": [],
    }
    
    try:
        with open(trace_file, 'r', encoding='utf-8') as f:
            for linea in f:
                evento = json.loads(linea)
                
                stats["total_events"] += 1
                event_type = evento.get('event_type', 'UNKNOWN')
                stats["by_type"][event_type] += 1
                
                component = evento.get('component', 'UNKNOWN')
                stats["by_component"][component] += 1
                
                # Registrar detecciones y comandos
                if event_type == "DETECTION":
                    stats["detections"].append({
                        "elapsed": evento.get('elapsed_seconds'),
                        "interseccion": evento.get('interseccion')
                    })
                elif event_type == "COMMAND":
                    stats["commands"].append({
                        "elapsed": evento.get('elapsed_seconds'),
                        "interseccion": evento.get('interseccion'),
                        "action": evento.get('details', {}).get('accion')
                    })
    
    except Exception as e:
        return {"error": str(e)}
    
    return dict(stats)

if __name__ == "__main__":
    print("[LOG_ANALYZER] Herramienta de análisis de logs cargada")
    print("Uso: analyzer = LogAnalyzer(); analyzer.extract_*(log_content)")
