# ÍNDICE COMPLETO - Sistema de Prueba y Métricas

## 📚 Documentación por Objetivo

### Si Quieres... → Lee Esto

**Ejecutar la prueba**
- ➡️ [TEST_SYSTEM.md](TEST_SYSTEM.md) - Instrucciones paso a paso

**Ejecutar prueba con métricas automáticas**
- ➡️ [run_test_with_metrics.py](run_test_with_metrics.py) - Script automatizado

**Entender las métricas rápidamente**
- ➡️ [METRICS_QUICK_START.md](METRICS_QUICK_START.md) - Guía de 5 minutos

**Aprender todas las métricas en detalle**
- ➡️ [METRICS_GUIDE.md](METRICS_GUIDE.md) - Documentación completa

**Ver resumen de métricas**
- ➡️ [METRICS_SUMMARY.md](METRICS_SUMMARY.md) - Resumen ejecutivo

**Entender la arquitectura del sistema**
- ➡️ [README.md](README.md) - Descripción completa del sistema

**Ver salida esperada de la prueba**
- ➡️ [EXPECTED_OUTPUT.md](EXPECTED_OUTPUT.md) - Logs esperados por terminal

**Validar que cumple requisitos**
- ➡️ [VALIDATION.md](VALIDATION.md) - Checklist de requisitos

**Entender cambios realizados**
- ➡️ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Resumen de cambios

---

## 🎯 Guía de Inicio Rápido

### 1️⃣ Ejecutar Prueba (3 minutos)

```bash
# Windows
.\run_test.ps1

# Linux/Mac
python run_test.py

# O con métricas automáticas (recomendado)
python run_test_with_metrics.py
```

### 2️⃣ Ver Resultados

```bash
# Buscar estos archivos después de ejecutar:
METRICS_REPORT.md          ← Resultados de todas las métricas
PC_3/db.json               ← Eventos en BD Principal
PC_2/db_replica.json       ← Eventos en BD Réplica
events_trace.jsonl         ← Trazas detalladas
```

### 3️⃣ Interpretar Resultados

```bash
# Abrir y leer METRICS_REPORT.md
cat METRICS_REPORT.md

# O leer METRICS_QUICK_START.md para interpretación rápida
cat METRICS_QUICK_START.md
```

---

## 📂 Estructura de Carpetas

```
Proyecto_Distribuidos/
│
├── DOCUMENTACIÓN PRINCIPAL
│   ├── README.md                    ← Inicio: Arquitectura y guía general
│   ├── TEST_SYSTEM.md              ← Cómo ejecutar la prueba
│   ├── EXPECTED_OUTPUT.md          ← Qué esperar ver
│   ├── VALIDATION.md               ← Validación de requisitos
│   └── IMPLEMENTATION_SUMMARY.md   ← Qué se implementó
│
├── SISTEMA DE MÉTRICAS
│   ├── METRICS_QUICK_START.md      ← LEER PRIMERO (5 min)
│   ├── METRICS_GUIDE.md            ← Guía detallada
│   ├── METRICS_SUMMARY.md          ← Resumen ejecutivo
│   ├── metrics.py                  ← Motor de cálculo
│   ├── event_tracker.py            ← Rastreador de eventos
│   └── analyze_logs.py             ← Analizador de logs
│
├── SCRIPTS DE EJECUCIÓN
│   ├── run_test_with_metrics.py    ← RECOMENDADO: Con métricas
│   ├── run_test.ps1                ← PowerShell (Windows)
│   ├── run_test.py                 ← Python (Multiplataforma)
│   └── sensores.py                 ← Generador de eventos
│
├── CONFIGURACIÓN
│   ├── config.py                   ← Configuración principal
│   ├── PC_1/
│   │   ├── broker_mq.py            ← Broker ZeroMQ
│   │   └── config.py               ← Config PC1
│   ├── PC_2/
│   │   ├── analisis.py             ← Servicio de analítica
│   │   ├── control_semaforos.py    ← Control de semáforos
│   │   ├── db_replica.py           ← BD réplica
│   │   └── config.py               ← Config PC2
│   └── PC_3/
│       ├── db.py                   ← BD principal
│       ├── consultas.py            ← Módulo de consultas
│       └── config.py               ← Config PC3
│
└── ARCHIVOS GENERADOS (después de ejecutar)
    ├── METRICS_REPORT.md           ← Reporte de métricas
    ├── events_trace.jsonl          ← Trazas de eventos
    ├── PC_3/db.json                ← Datos BD principal
    └── PC_2/db_replica.json        ← Datos BD réplica
```

---

## 🔍 Las 4 Métricas Clave

### Métrica 1: Eventos Almacenados
- **¿Qué mide?** Cuántos eventos llegaron a las BDs
- **Búscar en:** METRICS_REPORT.md → "Métrica 1"
- **Criterio:** BD Principal ≥80, BD Réplica ≥100
- **Archivos:** PC_3/db.json, PC_2/db_replica.json

### Métrica 2: Tiempo de Reacción
- **¿Qué mide?** Latencia detección → comando (ms)
- **Buscar en:** METRICS_REPORT.md → "Criterios de Evaluación"
- **Criterio:** Promedio <500ms, Máximo <2000ms
- **Archivos:** events_trace.jsonl

### Métrica 3: Eventos Especiales
- **¿Qué mide?** Detección correcta de congestión y ambulancias
- **Buscar en:** METRICS_REPORT.md → Checklist
- **Criterio:** Todas las detecciones correctas
- **Archivos:** Logs de consola

### Métrica 4: Tolerancia a Fallos
- **¿Qué mide?** Cambio a BD réplica cuando principal falla
- **Buscar en:** METRICS_REPORT.md → "Cronograma"
- **Criterio:** Fallover automático a los 140s
- **Archivos:** events_trace.jsonl, db.json, db_replica.json

---

## 🚀 Flujo Completo de Trabajo

```
1. PREPARACIÓN
   ├─ Instalar dependencias (zmq, pyzmq)
   └─ Leer README.md (5 min)

2. EJECUCIÓN
   ├─ Ejecutar: python run_test_with_metrics.py
   ├─ Esperar: 3 minutos (185 segundos)
   └─ Observar: 7 terminales con logs en tiempo real

3. RECOPILACIÓN AUTOMÁTICA
   ├─ Genera: METRICS_REPORT.md
   ├─ Genera: events_trace.jsonl
   └─ Copia: PC_3/db.json y PC_2/db_replica.json

4. INTERPRETACIÓN
   ├─ Leer: METRICS_REPORT.md (10 min)
   ├─ Verificar: Checklist de criterios
   └─ Analizar: Logs detallados si es necesario

5. DECISIÓN FINAL
   ├─ ✓ ACEPTABLE: Sistema operativo conforme
   ├─ ⚠ REVISAR: Algunos problemas identificados
   └─ ✗ FALLO: Problemas críticos
```

---

## 📊 Contenido de METRICS_REPORT.md

El reporte generado automáticamente contiene:

1. **Resumen Ejecutivo**
   - Fecha/hora
   - Duración de prueba
   - Estado del sistema

2. **Métrica 1: Eventos Almacenados**
   - Tabla de BD Principal vs Réplica
   - Desglose por tipo de sensor
   - Desglose por intersección (top 10)

3. **Métrica 2: Criterios de Evaluación**
   - Checklist de 10 criterios
   - Estado de cada uno (OK/ERROR)
   - Observaciones

4. **Cronograma de Eventos**
   - Tabla de eventos esperados vs observados
   - Tiempos de ocurrencia

5. **Conclusión**
   - Resumen de lo que demuestra el sistema
   - Evaluación final

---

## 🛠️ Herramientas de Análisis

### Herramienta 1: metrics.py
```python
from metrics import generate_metrics_report
generate_metrics_report()  # Genera reporte completo
```

### Herramienta 2: analyze_logs.py
```python
from analyze_logs import LogAnalyzer
analyzer = LogAnalyzer()
# Analizar logs de consola
```

### Herramienta 3: event_tracker.py
```python
from event_tracker import event_tracker
stats = event_tracker.get_report()
# Ver estadísticas de eventos
```

---

## ✅ Checklist de Éxito

Después de ejecutar, verificar:

- [ ] METRICS_REPORT.md generado
- [ ] DB Principal ≥ 80 eventos
- [ ] BD Réplica ≥ 100 eventos
- [ ] Latencia promedio < 500ms
- [ ] Congestión INT_2b detectada
- [ ] Congestión INT_3d detectada
- [ ] Ambulancias priorizadas
- [ ] Fallover BD a los 140s
- [ ] Todos los criterios = OK
- [ ] No hay errores críticos

---

## 📞 Preguntas Frecuentes

### P: ¿Por dónde empiezo?
**R:** 
1. Lee README.md (arquitectura)
2. Lee METRICS_QUICK_START.md (métricas)
3. Ejecuta `python run_test_with_metrics.py`
4. Lee METRICS_REPORT.md (resultados)

### P: ¿Cuánto tiempo tarda?
**R:** 
- Ejecución: ~3 minutos
- Lectura de documentación: ~15 minutos
- Total: ~20 minutos

### P: ¿Qué hago si algo falla?
**R:** 
1. Leer VALIDATION.md (checklist de requisitos)
2. Verificar logs de servicios en consolas
3. Revisar EXPECTED_OUTPUT.md
4. Ver archivo IMPLEMENTATION_SUMMARY.md

### P: ¿Cómo interpreto los resultados?
**R:** 
1. Abrir METRICS_REPORT.md
2. Seguir checklist de criterios
3. Leer METRICS_QUICK_START.md para cada métrica
4. Comparar con valores esperados

### P: ¿Qué archivos son importantes?
**R:**
- METRICS_REPORT.md ← PRINCIPAL
- events_trace.jsonl ← Detallado
- PC_2/db_replica.json ← Validación
- METRICS_QUICK_START.md ← Interpretación

---

## 🔗 Enlaces Rápidos

| Archivo | Tipo | Propósito |
|---------|------|----------|
| [README.md](README.md) | Docs | Inicio: Arquitectura |
| [METRICS_QUICK_START.md](METRICS_QUICK_START.md) | Docs | Métricas (5 min) |
| [METRICS_GUIDE.md](METRICS_GUIDE.md) | Docs | Métricas (completo) |
| [TEST_SYSTEM.md](TEST_SYSTEM.md) | Docs | Ejecución |
| [run_test_with_metrics.py](run_test_with_metrics.py) | Script | Ejecución recomendada |
| [metrics.py](metrics.py) | Código | Motor de métricas |
| [analyze_logs.py](analyze_logs.py) | Código | Análisis de logs |
| [VALIDATION.md](VALIDATION.md) | Docs | Validación requisitos |

---

## 📈 Estadísticas Esperadas

```
Métrica 1: Eventos Almacenados
├─ BD Principal:   80-90 eventos
├─ BD Réplica:    100-110 eventos
└─ Diferencia:     10-20 eventos (post-fallo)

Métrica 2: Tiempo de Reacción
├─ Promedio:      100-150ms
├─ Mínimo:         40-60ms
├─ Máximo:        150-300ms
└─ Aceptable si:   <500ms

Métrica 3: Eventos Especiales
├─ Congestión INT_2b: ✓ Detectada
├─ Congestión INT_3d: ✓ Detectada
├─ Ambulancia 1:      ✓ Prioritaria
└─ Ambulancia 2:      ✓ Prioritaria

Métrica 4: Tolerancia a Fallos
├─ Fallo detectado:   t≈140s ✓
├─ Cambio a réplica:  Automático ✓
├─ Eventos capturados: 10-20 post-fallo ✓
└─ Sin pérdida datos:  ✓
```

---

**Versión**: 1.0
**Última actualización**: 2026-05-28
**Estado**: ✓ Completo
