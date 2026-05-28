# GUÍA DE MÉTRICAS DE DESEMPEÑO

## Descripción General

Este documento describe el sistema de medición y evaluación del sistema distribuido de control de tráfico con ZeroMQ. Se proporciona un marco completo para medir desempeño, latencia y confiabilidad.

## Métricas Implementadas

### Métrica 1: Eventos Almacenados en Bases de Datos

**Objetivo**: Verificar que todos los eventos generados por sensores se almacenan correctamente en ambas bases de datos.

**Medición**:
- Se cuentan líneas válidas en `PC_3/db.json` (BD principal)
- Se cuentan líneas válidas en `PC_2/db_replica.json` (BD réplica)
- Período: 180+ segundos de prueba

**Fórmula**:
```
Total Eventos BD Principal = Número de líneas JSON válidas en db.json
Total Eventos BD Réplica = Número de líneas JSON válidas en db_replica.json
```

**Criterio de Éxito**:
- Mínimo 80 eventos en BD Principal (antes de t=140s)
- Mínimo 100+ eventos en BD Réplica (captura post-fallo)
- Diferencia BD Réplica > BD Principal (refleja fallover)

**Desglose por Tipo**:
```
Total Eventos = Eventos Cámara + Eventos Espira + Eventos GPS + Eventos Ambulancia
```

**Desglose por Intersección**:
```
Se contabilizan eventos por intersección específica:
- INT_2b: Mayor concentración durante 60-75s (congestión)
- INT_3d: Mayor concentración durante 95-110s (congestión)
- Fila 1: Mayor concentración durante 130-132s y 150-152s (ambulancias)
```

### Métrica 2: Tiempo de Reacción Analítica-Semáforo

**Objetivo**: Medir latencia desde detección de congestión hasta ejecución de comando en semáforo.

**Medición**:
- Registra tiempo exacto de detección de congestión en analítica
- Registra tiempo exacto de ejecución de comando en semáforo
- Calcula diferencia: Latencia = Tiempo Comando - Tiempo Detección

**Fórmula**:
```
Latencia Individual (ms) = (tiempo_comando - tiempo_detección) × 1000

Estadísticas Agregadas:
- Promedio = Σ Latencias / Número de detecciones
- Mínimo = Latencia más baja
- Máximo = Latencia más alta
- Desviación Estándar = √(Σ(x - promedio)² / n)
```

**Criterio de Éxito**:
- Latencia promedio < 500ms
- Latencia máxima < 2000ms
- Consistencia en todas las intersecciones

**Ejemplos de Cálculo**:
```
Escenario 1: Congestión en INT_2b (t=60s)
- Detección: t=60.1s
- Comando: t=60.2s
- Latencia: 100ms

Escenario 2: Congestión en INT_3d (t=95s)
- Detección: t=95.1s
- Comando: t=95.3s
- Latencia: 200ms

Promedio: (100 + 200) / 2 = 150ms
```

### Métrica 3: Cobertura de Intersecciones

**Objetivo**: Verificar que se procesan eventos de todas las intersecciones de la matriz 3x5.

**Medición**:
```
Total Intersecciones Esperadas = 15 (3 filas × 5 columnas)
Intersecciones con Eventos = Contar únicas en BD

Coverage (%) = (Intersecciones con Eventos / 15) × 100
```

**Criterio de Éxito**:
- Mínimo 80% de cobertura
- Especialmente: INT_2b, INT_3d, INT_1a-e deben estar presentes

### Métrica 4: Procesamiento de Eventos Especiales

**Criterio de Congestión**:
- Detección correcta cuando: volumen > 8 O velocidad < 15 km/h
- Acción: EXTENDER_VERDE por 10s adicionales

**Criterio de Ambulancia**:
- Prioridad máxima (CRÍTICA)
- Verde prioritario en toda la fila
- Se espera en t=130s y t=150s

**Criterio de Fallover BD**:
- BD Principal falla a t=140s exactamente
- BD Réplica captura eventos posterior a fallo
- No hay pérdida de datos entre t=140s-180s

## Herramientas de Medición

### 1. `metrics.py` - Recolector Principal

**Funciones clave**:
```python
count_events_in_file(filepath)
  → Cuenta eventos en archivo JSON
  → Retorna: total, errores, desglose por tipo e intersección

calculate_reaction_time(detections, commands, interseccion)
  → Calcula latencia detección → comando
  → Retorna: promedio, min, max, muestras

generate_metrics_report(output_file)
  → Genera reporte completo en Markdown
  → Incluye todas las métricas y criterios
```

### 2. `analyze_logs.py` - Análisis de Logs

**Funciones clave**:
```python
LogAnalyzer.extract_congestion_detections(log_content)
  → Busca líneas con "CONGESTION" en logs
  → Retorna: [(tiempo, interseccion), ...]

LogAnalyzer.extract_semaforo_commands(log_content)
  → Busca líneas con estado de semáforo
  → Retorna: [(tiempo, interseccion, accion), ...]

LogAnalyzer.calculate_reaction_times()
  → Empareja detecciones con comandos
  → Calcula latencias por intersección
```

### 3. `event_tracker.py` - Rastreador de Eventos

**Funciones clave**:
```python
event_tracker.log_event(event_type, component, interseccion, details)
  → Registra evento con timestamp preciso
  → Almacena en events_trace.jsonl

event_tracker.analyze_latencies(event_types_pair)
  → Analiza latencias entre dos tipos de eventos
  → Retorna: estadísticas por intersección
```

## Procedimiento de Medición

### Paso 1: Limpieza Inicial
```bash
# Remover datos antiguos
rm -f PC_3/db.json PC_2/db_replica.json events_trace.jsonl
```

### Paso 2: Ejecutar Prueba
```bash
python run_test_with_metrics.py
# O manualmente (ver TEST_SYSTEM.md)
```

### Paso 3: Recopilación Automática
El script `run_test_with_metrics.py`:
1. Inicia todos los servicios
2. Espera 185 segundos
3. Detiene automáticamente
4. Genera reporte METRICS_REPORT.md

### Paso 4: Análisis Manual (opcional)
```bash
python -c "
from metrics import generate_metrics_report
resultado = generate_metrics_report()
"
```

## Archivos de Salida

### 1. `METRICS_REPORT.md`
Reporte principal con:
- Métrica 1: Eventos almacenados
- Métrica 2: Tiempos de reacción
- Métrica 3: Cobertura de intersecciones
- Métrica 4: Criterios de evaluación
- Cronograma de eventos observados

### 2. `events_trace.jsonl`
Archivo de trazas con eventos individuales:
```json
{"timestamp": 1234567890.123, "elapsed_seconds": 60.1, "event_type": "DETECTION", "component": "ANALÍTICA", "interseccion": "INT_2b", "details": {...}}
```

### 3. `PC_3/db.json`
Eventos almacenados en BD Principal (hasta t=140s):
```json
{"sensor_id": "CAM-INT_1c", "tipo_sensor": "camara", "interseccion": "INT_1c", "estado": "NORMAL", ...}
```

### 4. `PC_2/db_replica.json`
Eventos almacenados en BD Réplica (completo, incluyendo post-fallo):
```json
{"sensor_id": "ESP-INT_2b", "tipo_sensor": "espira_inductiva", "interseccion": "INT_2b", "estado": "CONGESTION", ...}
```

## Criterios de Evaluación

### Desempeño Aceptable ✓

Se considera que el sistema presenta comportamiento aceptable si:

1. **Captura de Eventos** (Métrica 1):
   - [ ] BD Principal ≥ 80 eventos (antes de fallo)
   - [ ] BD Réplica ≥ 100 eventos (incluye post-fallo)
   - [ ] Diferencia BD Réplica > BD Principal ≥ 10 eventos

2. **Latencia Analítica-Semáforo** (Métrica 2):
   - [ ] Latencia promedio < 500ms
   - [ ] Latencia máxima < 2000ms
   - [ ] Todas las intersecciones < 1000ms

3. **Confiabilidad**:
   - [ ] Congestión INT_2b detectada correctamente a t≈60s
   - [ ] Congestión INT_3d detectada correctamente a t≈95s
   - [ ] Ambulancias priorizadas a t≈130s y t≈150s

4. **Tolerancia a Fallos**:
   - [ ] Fallo BD detectado a t≈140s
   - [ ] Fallover a BD Réplica automático
   - [ ] Eventos post-fallo capturados (140s-180s)

5. **Disponibilidad**:
   - [ ] Todos los servicios operativos en sus puertos
   - [ ] Comunicación ZeroMQ estable
   - [ ] Consultas PC3→PC2 recibidas periódicamente

## Interpretación de Resultados

### Escenario 1: Funcionamiento Normal
```
BD Principal:  90 eventos
BD Réplica:   105 eventos
Latencia promedio: 120ms
Cobertura: 13/15 intersecciones (86%)
Status: ✓ ACEPTABLE
```

### Escenario 2: Latencia Alta
```
Latencia promedio: 800ms
Latencia máxima: 2500ms
Status: ⚠ REQUIERE OPTIMIZACIÓN
Acciones: Verificar CPU, reducir carga
```

### Escenario 3: Pérdida de Datos
```
BD Principal:  50 eventos (esperados: 90)
BD Réplica:   100 eventos
Diferencia: Posible pérdida pre-fallo
Status: ✗ PROBLEMA DE CAPTURA
Acciones: Verificar conexiones ZMQ
```

## Mejoras Futuras

1. Monitoreo en tiempo real de latencias
2. Alertas si se exceden umbrales
3. Gráficos de distribución de eventos
4. Análisis de patrones de congestión
5. Predicción de tiempos de respuesta

## Referencias

- Métrica 1: Confiabilidad y Capacidad de Almacenamiento
- Métrica 2: Latencia de Toma de Decisiones
- Métrica 3: Cobertura del Sistema
- Métrica 4: Correctitud de Clasificación

---

**Versión**: 1.0
**Última actualización**: 2026-05-28
**Estado**: Completo y listo para uso
