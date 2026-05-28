# GUÍA VISUAL DE FLUJO - Sistema de Métricas

## Flujo de Ejecución y Medición

```
┌─────────────────────────────────────────────────────────────┐
│            SISTEMA DE PRUEBA CON MÉTRICAS                   │
└─────────────────────────────────────────────────────────────┘

FASE 1: PREPARACIÓN
├─ ✓ Instalar dependencias (zmq, pyzmq)
├─ ✓ Revisar config.py (DB_FAILURE_TIME=140)
├─ ✓ Limpiar datos antiguos (db.json, db_replica.json)
└─ ✓ Abrir 7 terminales (una por servicio)

FASE 2: INICIAR SERVICIOS (En Orden)
├─ Terminal 1: python PC_1/broker_mq.py        [PUERTO 5557]
├─ Terminal 2: python sensores.py              [START]
├─ Terminal 3: python PC_2/analisis.py         [PUERTO 5558-5561]
├─ Terminal 4: python PC_2/control_semaforos.py[PUERTO 5559]
├─ Terminal 5: python PC_2/db_replica.py       [PUERTO 5560]
├─ Terminal 6: python PC_3/db.py               [PUERTO 5558]
└─ Terminal 7: python PC_3/consultas.py        [PUERTO 5561]

[ESPERAR 185 SEGUNDOS]

FASE 3: EVENTOS ESPERADOS
├─ t=30s:   Consulta: estado_general
├─ t=45s:   Consulta: eventos_congestion
├─ t=60s:   [CONGESTIÓN] INT_2b detectada
│           └─ Comando: VERDE_EXTENDIDO (10s)
├─ t=80s:   Comando directo de usuario
├─ t=95s:   [CONGESTIÓN] INT_3d detectada
│           └─ Comando: VERDE_EXTENDIDO (10s)
├─ t=130s:  [AMBULANCIA 1] Detectada
│           └─ Comando: VERDE PRIORITARIO
├─ t=140s:  [FALLO] BD Principal offline
│           └─ Cambio automático a BD Réplica
├─ t=150s:  [AMBULANCIA 2] Detectada
│           └─ Comando: VERDE PRIORITARIO
└─ t=180s:  [STOP] Fin de prueba

FASE 4: RECOPILACIÓN DE MÉTRICAS
├─ Contar eventos en archivos
├─ Calcular tiempos de reacción
├─ Verificar criterios especiales
├─ Generar reporte METRICS_REPORT.md
└─ Crear trace de eventos: events_trace.jsonl

FASE 5: ANÁLISIS Y EVALUACIÓN
├─ Leer: METRICS_REPORT.md
├─ Verificar: Todos los criterios ✓
├─ Validar: Eventos en archivos
└─ Conclusión: ✓ ACEPTABLE / ⚠ REVISAR / ✗ FALLO
```

---

## Diagrama de Componentes

```
                        ┌──────────────┐
                        │   SENSORES   │
                        │ (Generador)  │
                        └────────┬─────┘
                                 │ PUB
                                 ▼
                        ┌──────────────┐
                   ┌───►│   BROKER     │◄────┐
                   │    │  (PC1:5556)  │     │
                   │    └──────┬───────┘     │
                   │           │ PUB         │
                   │           ▼             │
        ┌──────────┴───────┬────────┬──────┴─────┐
        │                  │        │            │
        ▼                  ▼        ▼            ▼
    ┌────────┐          ┌────────┐  ┌──────┐  ┌───────┐
    │ ANALÍ- │          │SEMÁFO- │  │ BD   │  │ QUERY │
    │ TICA   │─PUSH─→ │ ROS    │  │RÉPLICA  │ REQUEST│
    │(PC2)   │        │(PC2)   │  │(PC2) │  │(PC3)  │
    └───┬─┬──┘        └────────┘  └──────┘  └───────┘
        │ │ PUSH
        │ ▼                ▼
        │ ┌───────────────────┐
        │ │  BD PRINCIPAL     │
        │ │  (PC3:5558)       │
        │ │  Status: Falla@140s
        │ └───────────────────┘
        │
        ▼
    ┌─────────────────────────┐
    │  MÉTRICA 1: EVENTOS     │
    │  ├─ Principal: 80-90    │
    │  ├─ Réplica:   100-110  │
    │  └─ Diferencia: 10-20   │
    └─────────────────────────┘

    ┌─────────────────────────┐
    │  MÉTRICA 2: LATENCIA    │
    │  ├─ Promedio: 100-150ms │
    │  ├─ Máximo: <500ms      │
    │  └─ Rango: 40-300ms     │
    └─────────────────────────┘

    ┌─────────────────────────┐
    │  MÉTRICA 3: ESPECIALES  │
    │  ├─ Congestión: ✓✓      │
    │  └─ Ambulancias: ✓✓     │
    └─────────────────────────┘

    ┌─────────────────────────┐
    │  MÉTRICA 4: FALLOVER    │
    │  ├─ Fallo: t=140s ✓     │
    │  ├─ Cambio: Auto ✓      │
    │  └─ Datos: Capturados ✓ │
    └─────────────────────────┘
```

---

## Cronograma Detallado

```
TIEMPO  EVENTO                          MÉTRICA          ARCHIVO
─────────────────────────────────────────────────────────────────
0s      Sistema inicia
        ├─ Broker activo
        ├─ Sensores generando
        └─ Servicios escuchando

30s     Consulta: estado_general       [3] Especiales   events_trace.jsonl
        └─ PC3 → PC2 (PUSH/PULL)

45s     Consulta: eventos_congestion   [3] Especiales   events_trace.jsonl
        └─ PC3 → PC2 (PUSH/PULL)

60s     ★ CONGESTIÓN INT_2b            [1] Eventos      db.json
        ├─ Detección: ANALÍTICA        [2] Latencia     events_trace.jsonl
        ├─ Comando: VERDE_EXTENDIDO
        └─ Duración: 10 segundos

80s     Comando: INT_1b → VERDE        [3] Especiales   events_trace.jsonl
        └─ Desde consulta PC3

95s     ★ CONGESTIÓN INT_3d            [1] Eventos      db.json
        ├─ Detección: ANALÍTICA        [2] Latencia     events_trace.jsonl
        ├─ Comando: VERDE_EXTENDIDO
        └─ Duración: 10 segundos

130s    ★ AMBULANCIA 1 (Fila 1)        [1] Eventos      db.json
        ├─ Prioridad: CRÍTICA          [3] Especiales   events_trace.jsonl
        ├─ Comando: VERDE PRIORITARIO
        └─ Duración: Máxima

140s    ⚠️  FALLO DE BD PRINCIPAL       [4] Fallover     events_trace.jsonl
        ├─ BD (PC3) OFFLINE
        ├─ SWITCH: Analítica → Réplica
        └─ BD Réplica ACTIVA

150s    ★ AMBULANCIA 2 (Fila 1)        [1] Eventos      db_replica.json
        ├─ Prioridad: CRÍTICA          [3] Especiales   events_trace.jsonl
        ├─ Comando: VERDE PRIORITARIO
        └─ Duración: Máxima

180s+   ✓ FIN DE PRUEBA               [1][2][3][4]     METRICS_REPORT.md
        ├─ Recopilación automática
        ├─ Generación de reporte
        └─ Datos guardados
```

---

## Árbol de Decisión de Evaluación

```
                    ¿PRUEBA EJECUTADA?
                           │
                 ┌─────────┴─────────┐
                 NO                  SÍ
                 │                   │
            [ERROR]         ¿METRICS_REPORT.md?
            Ver:                     │
            TEST_SYSTEM.md      ┌────┴────┐
                               NO        SÍ
                               │         │
                           [ERROR]  ¿BD Principal
                           Ver:     ≥80 eventos?
                           config.py│
                                ┌───┴───┐
                               NO      SÍ
                               │       │
                         [ERROR]   ¿BD Réplica
                         Ver:      ≥100 eventos?
                         sensores.py│
                             ┌──────┴──────┐
                            NO            SÍ
                            │             │
                      [ERROR]         ¿Latencia
                      Ver:            promedio
                      analisis.py     <500ms?
                                      │
                                 ┌────┴────┐
                                NO        SÍ
                                │         │
                          [ERROR]     ¿Congestión
                          Ver:        INT_2b+INT_3d
                          Logs        detectadas?
                                      │
                                 ┌────┴────┐
                                NO        SÍ
                                │         │
                          [ERROR]     ¿Ambulancias
                          Ver:        priorizadas?
                          Logs        │
                                 ┌────┴────┐
                                NO        SÍ
                                │         │
                          [ERROR]     ¿Fallover BD
                          Ver:        automático?
                          config.py   │
                                 ┌────┴────┐
                                NO        SÍ
                                │         │
                          [ERROR]    ✓ ACEPTABLE
                          Ver:       [Todos OK]
                          db.py
```

---

## Archivos Generados y Ubicación

```
Proyecto_Distribuidos/
│
├─ MÉTRICAS GENERADAS
│  ├─ METRICS_REPORT.md              ← LEER PRIMERO
│  ├─ events_trace.jsonl             ← Detallado
│  └─ LOG_ANALYSIS_REPORT.md         ← Análisis logs
│
├─ DATOS PERSISTIDOS
│  ├─ PC_3/db.json                   ← BD Principal (~90 eventos)
│  └─ PC_2/db_replica.json           ← BD Réplica (~105 eventos)
│
└─ DOCUMENTACIÓN
   ├─ METRICS_QUICK_START.md         ← Guía rápida (5 min)
   ├─ METRICS_GUIDE.md               ← Completa
   ├─ METRICS_SUMMARY.md             ← Ejecutivo
   └─ METRICS_CHEATSHEET.md          ← 1 página
```

---

## Interpretación de Resultados

```
Paso 1: ¿Cuántos eventos en BD?
├─ Principal < 50        → [PROBLEMA] Sensores no funcionan
├─ Principal 80-90       → ✓ OK (normal)
├─ Réplica < 100         → [PROBLEMA] Réplica no recibe
└─ Réplica > Principal   → ✓ OK (post-fallo)

Paso 2: ¿Latencia?
├─ < 200ms              → ✓ EXCELENTE
├─ 200-500ms            → ✓ ACEPTABLE
├─ 500-2000ms           → ⚠ REVISAR
└─ > 2000ms             → ✗ CRÍTICO

Paso 3: ¿Eventos especiales?
├─ INT_2b congestión @ 60s   → ✓ OK
├─ INT_3d congestión @ 95s   → ✓ OK
├─ Ambulancia 1 @ 130s       → ✓ OK
└─ Ambulancia 2 @ 150s       → ✓ OK

Paso 4: ¿Fallover?
├─ Cambio @ 140s exacto      → ✓ OK
├─ BD Réplica recibe post    → ✓ OK
├─ Sin pérdida de datos      → ✓ OK
└─ Todos OK = ✓ ACEPTABLE
```

---

## Verificación Rápida (30 segundos)

```bash
# 1. ¿Existen archivos?
ls -l METRICS_REPORT.md events_trace.jsonl

# 2. ¿Cuántos eventos?
wc -l PC_3/db.json PC_2/db_replica.json

# 3. ¿Qué dicen los archivos?
head -5 METRICS_REPORT.md

# 4. ¿BD creció post-fallo?
tail -5 PC_2/db_replica.json

# RESULTADO: ✓ ACEPTABLE / ⚠ REVISAR / ✗ FALLO
```

---

**Referencia Visual Rápida**  
*Imprime esta página como guía durante las pruebas*

Versión: 1.0 | Estado: ✓ Completo | Última actualización: 2026-05-28
