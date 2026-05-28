# SISTEMA DE MEDICIÓN DE DESEMPEÑO - RESUMEN EJECUTIVO

## Información General

**Sistema**: Control de Tráfico Distribuido con ZeroMQ
**Propósito**: Medir desempeño, latencia y confiabilidad
**Documentos de referencia**: METRICS_GUIDE.md, METRICS_QUICK_START.md

## Las 4 Métricas Principales

### Métrica 1: Eventos Almacenados en Dos Minutos

**Definición:**
Contar eventos persistidos en BD principal y réplica durante la ventana de prueba (180+ segundos)

**Implementación:**
```python
# En metrics.py
count_events_in_file("PC_3/db.json")      # BD Principal
count_events_in_file("PC_2/db_replica.json")  # BD Réplica
```

**Medición:**
- Cuenta líneas JSON válidas en archivos
- Desglosa por tipo de sensor (cámara, espira, GPS, ambulancia)
- Desglosa por intersección específica
- Calcula ratio BD Réplica / BD Principal

**Criterio de Éxito:**
```
BD Principal ≥ 80 eventos (hasta t=140s)
BD Réplica ≥ 100 eventos (incluye post-fallo)
Diferencia ≥ 10 eventos (post-fallo capturados)
```

**Archivos de Salida:**
- `METRICS_REPORT.md` → Sección "Métrica 1"
- `PC_3/db.json` (BD Principal)
- `PC_2/db_replica.json` (BD Réplica)

---

### Métrica 2: Tiempo de Reacción Analítica → Semáforo

**Definición:**
Latencia desde detección de congestión hasta ejecución de comando en semáforo

**Implementación:**
```python
# En analyze_logs.py
LogAnalyzer.extract_congestion_detections()  # Obtiene tiempos de detección
LogAnalyzer.extract_semaforo_commands()      # Obtiene tiempos de comando
LogAnalyzer.calculate_reaction_times()       # Calcula diferencia
```

**Medición:**
- Timestamps precisos desde logs de consola
- Empareja detecciones con comandos por intersección
- Calcula promedio, mínimo, máximo

**Fórmula:**
```
Latencia (ms) = (tiempo_comando - tiempo_detección) × 1000

Estadísticas:
- Promedio: Σ latencias / número de pares
- Mínimo: latencia más baja
- Máximo: latencia más alta
```

**Criterio de Éxito:**
```
Promedio < 500ms
Máximo < 2000ms
Consistencia en todas las intersecciones
```

**Ejemplo Real:**
```
Detección (ANALÍTICA): [60.1s] CONGESTION detectada en INT_2b
Comando (SEMÁFOROS): [60.2s] Estado: VERDE_EXTENDIDO
Latencia: (60.2 - 60.1) × 1000 = 100ms ✓
```

**Archivos de Salida:**
- `METRICS_REPORT.md` → Sección "Criterios de Evaluación"
- `events_trace.jsonl` (timestamps precisos)

---

### Métrica 3: Eventos Especiales (Congestión, Ambulancias)

**Definición:**
Verificar que eventos especiales se procesan correctamente según reglas

**Reglas de Detección:**

**Congestión:**
```
CAMARA:  volumen > 8 O velocidad < 15 km/h
ESPIRA:  vehiculos_contados > 15
GPS:     velocidad < 10 km/h
```

**Ambulancia:**
```
Prioridad: CRÍTICA
Acción: VERDE_AMBULANCIA en toda la fila
Duración: Máxima (hasta que pase)
```

**Criterio de Éxito:**
```
INT_2b: congestión detectada a t=60-75s
INT_3d: congestión detectada a t=95-110s
Fila 1: ambulancia con verde prioritario a t=130s y t=150s
```

**Verificación en Logs:**
```
CONGESTIÓN:
[60.1s] [ANALÍTICA] CONGESTION detectada en INT_2b
[60.1s] [SEMÁFOROS] [OK] Estado: VERDE_EXTENDIDO ✓

AMBULANCIA:
[130.2s] AMBULANCIA DETECTADA A LOS 130.2s
[130.2s] [SEMÁFOROS] [OK] Estado: VERDE PRIORITARIO ✓
```

---

### Métrica 4: Tolerancia a Fallos (Fallover de BD)

**Definición:**
Cambio automático de BD Principal a Réplica cuando la primera falla

**Evento Crítico:**
```
Tiempo: t = 140 segundos (exacto)
Acción: BD Principal (PC3) falla
Respuesta: Analítica cambia a BD Réplica (PC2)
Verificación: Eventos posteriores capturados en réplica
```

**Verificación en Logs:**
```
[140.0s] FALLO DE BD PRINCIPAL EN PC3
[140.0s] Cambiando a BD RÉPLICA en PC2
[140.0s] BD PRINCIPAL OFFLINE - Usando BD RÉPLICA

Después de 140s:
- BD Réplica sigue recibiendo eventos ✓
- BD Principal no recibe eventos ✓
```

**Criterio de Éxito:**
```
Detección automática en t≈140s
Cambio sin interrución de servicio
Eventos capturados después del fallo
Diferencia eventos > 10 (post-fallo)
```

**Archivos Afectados:**
- `PC_3/db.json` - Se detiene en ~140s
- `PC_2/db_replica.json` - Continúa después de 140s
- `METRICS_REPORT.md` → Sección "Cronograma"

---

## Herramientas de Medición

### 1. Salidas por Consola

**Componentes:**
- SENSORES: Genera eventos con timestamps
- ANALÍTICA: Detecta y registra congestiones
- SEMÁFOROS: Ejecuta comandos y registra
- BD PRINCIPAL/RÉPLICA: Guardan eventos
- CONSULTAS: Envían queries periódicas

**Información Clave en Logs:**
```
[tiempo_s] [COMPONENTE] [OK/ERROR] Descripción del evento
```

### 2. Archivos de Persistencia

**BD Principal:** `PC_3/db.json`
```json
{"sensor_id": "CAM-INT_2b", "tipo_sensor": "camara", "estado": "CONGESTION"}
```

**BD Réplica:** `PC_2/db_replica.json`
```json
{"sensor_id": "ESP-INT_3d", "tipo_sensor": "espira_inductiva", "estado": "CONGESTION"}
```

**Trace de Eventos:** `events_trace.jsonl`
```json
{"elapsed_seconds": 60.1, "event_type": "DETECTION", "interseccion": "INT_2b"}
{"elapsed_seconds": 60.2, "event_type": "COMMAND", "interseccion": "INT_2b"}
```

### 3. Conteo de Registros

**Script Python:**
```python
from metrics import count_events_in_file

db_principal = count_events_in_file("PC_3/db.json")
print(f"Eventos principal: {db_principal['eventos_totales']}")

db_replica = count_events_in_file("PC_2/db_replica.json")
print(f"Eventos réplica: {db_replica['eventos_totales']}")
```

### 4. Comparación de Eventos

**Eventos Procesados vs Comandos Ejecutados:**
```
Detecciones de Congestión: 22 eventos
Comandos de Semáforo: 22 comandos
Ratio: 100% (1:1 correspondencia) ✓

Eventos Almacenados: 95 eventos
Ratio Almacenamiento: 100% ✓
```

---

## Criterios de Evaluación

### ✓ Comportamiento Aceptable

**Checklist:**
```
1. Eventos generados por sensores llegan a analítica
   ✓ Mínimo 80 eventos en BD principal
   ✓ Mínimo 100 eventos en BD réplica

2. Analítica clasifica correctamente
   ✓ Congestión detectada en INT_2b (60-75s)
   ✓ Congestión detectada en INT_3d (95-110s)
   ✓ Ambulancias priorizadas

3. Eventos procesados en repositorios
   ✓ Datos en BD principal (hasta 140s)
   ✓ Datos en BD réplica (continuo)
   ✓ Sin pérdida de información

4. Comandos llegan a semáforos
   ✓ EXTENDER_VERDE ejecutado
   ✓ VERDE_AMBULANCIA ejecutado
   ✓ Cambios visibles en logs

5. Tiempos de respuesta consistentes
   ✓ Latencia promedio < 500ms
   ✓ Latencia máxima < 2000ms
   ✓ Sin spikes excepcionales
```

### Umbral de Latencia

| Categoría | Rango | Estado |
|-----------|-------|--------|
| Excelente | < 100ms | ✓ Óptimo |
| Bueno | 100-300ms | ✓ Aceptable |
| Aceptable | 300-500ms | ✓ Normal |
| Degradado | 500-2000ms | ⚠ Revisar |
| Crítico | > 2000ms | ✗ Error |

---

## Procedimiento Completo de Medición

### Fase 1: Preparación
```bash
# Limpiar datos antiguos
rm -f PC_3/db.json PC_2/db_replica.json events_trace.jsonl

# Verificar configuración
cat config.py | grep DB_FAILURE_TIME  # Debe ser 140
```

### Fase 2: Ejecución
```bash
# Opción 1: Automatizado
python run_test_with_metrics.py

# Opción 2: Manual (ver TEST_SYSTEM.md)
# Abrir 7 terminales y ejecutar servicios
```

### Fase 3: Recopilación
```bash
# El script captura automáticamente:
# - Archivos db.json y db_replica.json
# - Logs de consola (manual)
# - Timestamps de eventos
```

### Fase 4: Análisis
```bash
# Reporte automático se genera al completar:
# → METRICS_REPORT.md

# Análisis manual (opcional):
python -c "
from metrics import generate_metrics_report
resultado = generate_metrics_report()
print('Reporte generado')
"
```

### Fase 5: Interpretación
```bash
# Leer METRICS_REPORT.md
cat METRICS_REPORT.md | head -100

# Verificar archivos de datos
wc -l PC_3/db.json PC_2/db_replica.json

# Análisis de latencias
python analyze_logs.py
```

---

## Archivos Generados y Su Contenido

### `METRICS_REPORT.md`
**Contenido:**
- Resumen ejecutivo
- Métrica 1: Eventos almacenados (tabla de stats)
- Métrica 2: Criterios de evaluación (checklist)
- Cronograma de eventos observados
- Conclusión

**Usar para:** Evaluación rápida del sistema

### `events_trace.jsonl`
**Contenido:**
- Línea por evento: timestamp, tipo, componente, detalles
- Formato: JSON Lines (una línea por evento)

**Usar para:** Análisis detallado de latencias

### `PC_3/db.json`
**Contenido:**
- Eventos almacenados en BD principal
- ~87 eventos (se detiene a los 140s)

**Usar para:** Verificación de datos pre-fallo

### `PC_2/db_replica.json`
**Contenido:**
- Todos los eventos capturados
- ~105+ eventos (incluye post-fallo)

**Usar para:** Verificación de fallover

---

## Interpretación de Resultados

### Escenario Típico (Correcto)

```
MÉTRICA 1: Eventos Almacenados
- BD Principal: 87 eventos ✓
- BD Réplica: 108 eventos ✓
- Diferencia: 21 eventos (post-fallo) ✓

MÉTRICA 2: Tiempo de Reacción
- Promedio: 105ms ✓
- Mínimo: 42ms ✓
- Máximo: 195ms ✓

MÉTRICA 3: Eventos Especiales
- Congestión INT_2b: Detectada ✓
- Congestión INT_3d: Detectada ✓
- Ambulancia Fila 1: Prioritaria ✓

MÉTRICA 4: Fallover BD
- Fallo detectado: t=140s ✓
- Cambio a réplica: Automático ✓
- Eventos post-fallo: Capturados ✓

RESULTADO: ✓ SISTEMA OPERATIVO
```

### Escenario Problemático (Revisión Necesaria)

```
MÉTRICA 1: Eventos Almacenados
- BD Principal: 30 eventos ⚠ (esperado: 80+)
- BD Réplica: 40 eventos ⚠ (esperado: 100+)
→ Problema: Sensores o Broker no funcionando

MÉTRICA 2: Tiempo de Reacción
- Promedio: 2500ms ⚠ (esperado: <500ms)
→ Problema: CPU saturada o proceso bloqueado

MÉTRICA 3: Eventos Especiales
- Congestión INT_2b: NO detectada ✗
→ Problema: Reglas incorrectas o evento no llegó

MÉTRICA 4: Fallover BD
- Fallo NO detectado a los 140s ✗
- BD Réplica nunca se activó ✗
→ Problema: Fallover configuración incorrecta

RESULTADO: ✗ REQUIERE DEBUGGING
```

---

## Cómo Usar Este Sistema

### Para Verificación Rápida
1. Ejecutar `run_test_with_metrics.py`
2. Esperar 3 minutos
3. Abrir `METRICS_REPORT.md`
4. Verificar checklist de criterios

### Para Análisis Detallado
1. Guardar logs de consola de cada servicio
2. Ejecutar `analyze_logs.py` con logs
3. Revisar `events_trace.jsonl`
4. Calcular latencias manualmente si es necesario

### Para Debugging
1. Activar logs detallados en código
2. Registrar eventos con `event_tracker.log_event()`
3. Analizar `events_trace.jsonl` línea por línea
4. Comparar con logs de consola

---

## Referencias

- **Requisito Original**: IX-A, IX-B, IX-C, IX-D del documento de prueba
- **Documentación**: METRICS_GUIDE.md, METRICS_QUICK_START.md
- **Código**: metrics.py, event_tracker.py, analyze_logs.py
- **Scripts**: run_test_with_metrics.py

---

**Versión**: 1.0
**Estado**: ✓ Completo
**Última actualización**: 2026-05-28
