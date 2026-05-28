# CHEAT SHEET - Sistema de Métricas (1 página)

## INICIO RÁPIDO (3 pasos)

```bash
1. EJECUTAR:
   python run_test_with_metrics.py

2. ESPERAR:
   3 minutos (185 segundos)

3. LEER:
   METRICS_REPORT.md
```

---

## LAS 4 MÉTRICAS

| Métrica | Mide | Criterio | Archivo |
|---------|------|----------|---------|
| **1: Eventos** | Cuántos eventos guardados | BD Principal ≥80<br/>BD Réplica ≥100 | db.json, db_replica.json |
| **2: Latencia** | Tiempo detección→comando (ms) | Promedio <500ms<br/>Máximo <2000ms | events_trace.jsonl |
| **3: Especiales** | Congestión y ambulancias | INT_2b, INT_3d, Ambulancias ✓ | Logs consola |
| **4: Fallover** | Cambio automático a BD réplica | t=140s automático | db.json vs db_replica.json |

---

## INTERPRETACIÓN RÁPIDA

### BD Principal
```json
- Eventos: 80-90 (normal)
- Tiempo: detiene en ~140s (fallo)
- Archivo: PC_3/db.json
```

### BD Réplica
```json
- Eventos: 100-110 (más que principal)
- Tiempo: continúa después de 140s
- Archivo: PC_2/db_replica.json
- Diferencia: 10-20 eventos post-fallo
```

### Latencia
```
Promedio: 100-300ms (normal)
Máximo: <1000ms (aceptable)
Rango crítico: >2000ms (error)
```

### Cronograma
```
60s:   Congestión INT_2b detectada
95s:   Congestión INT_3d detectada
130s:  Ambulancia 1 con prioridad
140s:  BD Principal falla → Réplica activa
150s:  Ambulancia 2 con prioridad
180s:  Fin de prueba
```

---

## CHECKLIST DE ÉXITO ✓

```
MÉTRICA 1: Eventos Almacenados
☐ BD Principal ≥ 80 eventos
☐ BD Réplica ≥ 100 eventos
☐ Diferencia ≥ 10 eventos

MÉTRICA 2: Latencia
☐ Promedio < 500ms
☐ Máximo < 2000ms
☐ Consistencia entre intersecciones

MÉTRICA 3: Eventos Especiales
☐ Congestión INT_2b detectada (60s)
☐ Congestión INT_3d detectada (95s)
☐ Ambulancia 1 prioritaria (130s)
☐ Ambulancia 2 prioritaria (150s)

MÉTRICA 4: Fallover
☐ Fallo detectado a t≈140s
☐ Cambio a BD Réplica automático
☐ Eventos post-fallo capturados

RESULTADO:
☐ Todos los criterios OK = ✓ ACEPTABLE
```

---

## ARCHIVOS CLAVE

**Después de ejecutar, buscar:**

1. **METRICS_REPORT.md** ← LEER PRIMERO
   - Reporte completo con todas las métricas
   - Checklist de evaluación

2. **events_trace.jsonl** ← Detalles
   - Timestamps precisos de eventos
   - Para análisis detallado

3. **PC_3/db.json** ← Validación
   - Eventos BD Principal
   - Deberá tener ~80-90 eventos

4. **PC_2/db_replica.json** ← Validación
   - Eventos BD Réplica
   - Deberá tener ~100-110 eventos

---

## DIAGNÓSTICO RÁPIDO

### Problema: 0 eventos
```
Verificar:
1. ¿Broker corriendo? netstat -an | grep 5556
2. ¿Sensores enviando? Revisar logs
3. ¿BD escuchando? netstat -an | grep 5558
→ Solución: Ver VALIDATION.md
```

### Problema: Latencia > 5000ms
```
Verificar:
1. CPU disponible? (Task Manager)
2. ZMQ conectado? (netstat)
3. Errores en logs?
→ Solución: Revisar consolas de servicios
```

### Problema: BD Réplica igual a Principal
```
Verificar:
1. ¿Prueba interrumpida antes de 140s?
2. ¿BD Réplica realmente recibiendo post-fallo?
3. ¿Timestamp de fallo correcto (140)?
→ Solución: Ver config.py - DB_FAILURE_TIME
```

---

## ESTADÍSTICAS ESPERADAS

```
Sensores Generados:  ~90-100 eventos totales
BD Principal:        ~80-90 eventos (antes 140s)
BD Réplica:          ~100-110 eventos (después 140s)
Latencia Promedio:   100-150 ms
Latencia Máximo:     <500 ms (aceptable)
Congestiones:        2 (INT_2b, INT_3d)
Ambulancias:         2 (con prioridad)
Fallover BD:         Automático a 140s
```

---

## DOCUMENTACIÓN RELACIONADA

- **README.md** → Arquitectura del sistema
- **METRICS_QUICK_START.md** → Métricas (detallado)
- **METRICS_GUIDE.md** → Especificación completa
- **TEST_SYSTEM.md** → Cómo ejecutar
- **VALIDATION.md** → Checklist de requisitos
- **EXPECTED_OUTPUT.md** → Qué ver en logs

---

## HERRAMIENTAS

```python
# Generar reporte manualmente
python -c "from metrics import generate_metrics_report; generate_metrics_report()"

# Analizar logs
python analyze_logs.py

# Ver estadísticas de eventos
python -c "from event_tracker import event_tracker; print(event_tracker.get_report())"

# Contar eventos en archivo
python -c "from metrics import count_events_in_file; print(count_events_in_file('PC_2/db_replica.json'))"
```

---

## CONTACTO / PREGUNTAS

**¿No entiendo los resultados?**
→ Ver METRICS_QUICK_START.md

**¿Algo falló?**
→ Ver VALIDATION.md + EXPECTED_OUTPUT.md

**¿Necesito detalle completo?**
→ Ver METRICS_GUIDE.md

**¿Cómo ejecuto?**
→ Ver TEST_SYSTEM.md

---

**Versión**: 1.0  |  **Estado**: ✓ Completo  |  **Última actualización**: 2026-05-28

---

## MAPA MENTAL DEL SISTEMA

```
SENSORES (3-5 min)
    ↓
EVENTOS (90-100 eventos)
    ↓
BROKER ZMQ
    ├─→ ANALÍTICA
    │    ├─ Detecta: Congestión
    │    ├─ Detecta: Ambulancia
    │    ├─ Acciona: Semáforos
    │    └─ Guarda: BD (con fallover)
    │
    └─→ SEMÁFOROS
         ├─ Recibe: EXTENDER_VERDE
         ├─ Recibe: VERDE_AMBULANCIA
         └─ Ejecuta: Comandos
    
BD PRIMARY (PC_3)
    ├─ 0-140s: Recibe eventos (~80)
    └─ 140s+: OFFLINE (error simulado)

BD REPLICA (PC_2)
    ├─ 0-140s: Recibe eventos (~80)
    └─ 140s+: ACTIVA (recibe 100+)

RESULTADO: ✓ 2 fases evaluadas
  Fase 1 (0-140s): Operación normal
  Fase 2 (140-180s): Tolerancia a fallos
```

---

**Imprime esta página como referencia durante las pruebas**
