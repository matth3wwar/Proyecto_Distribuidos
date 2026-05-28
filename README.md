# Sistema de Control de Tráfico Distribuido con ZeroMQ

## Descripción General

Sistema distribuido que simula el control de semáforos en una ciudad de **3x5 intersecciones** (15 intersecciones totales) con comunicación asíncrona mediante ZeroMQ. El sistema incluye detección de congestiones, manejo de ambulancias con prioridad crítica, fallover de base de datos y consultas en tiempo real.

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                      SIMULACIÓN                          │
│  sensores.py (Generador de eventos)                     │
│  - Envía eventos de sensores de tráfico                 │
│  - Simula congestiones en tiempos específicos           │
│  - Genera solicitudes de ambulancias                     │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────▼────────┐
        │   PC1: BROKER    │
        │   (PUERTO 5556)  │
        │                  │
        │  PUB/SUB Bridge  │
        │                  │
        └─────────┬────────┘
                  │
        ┌─────────▼────────────────────────────────────────┐
        │                                                   │
  ┌─────▼──────────────┐        ┌──────────────────┐     │
  │   PC2: SERVICIOS   │        │  PC3: CONSULTAS  │     │
  │                    │        │  Y BASE DE DATOS │     │
  ├────────────────────┤        ├──────────────────┤     │
  │ analisis.py        │        │ consultas.py     │     │
  │ (Análisis/eventos) │        │ (Queries→PC2)    │     │
  │                    │        │                  │     │
  │ control_semaforos  │        │ db.py (BD Ppal)  │     │
  │ (Estado semáforos) │        │ Falla a los 140s │     │
  │                    │        │                  │     │
  │ db_replica.py      │        └──────────────────┘     │
  │ (BD backup)        │                                  │
  │                    │        ┌──────────────────┐     │
  └────────────────────┘        │  TIMEOUTS Y      │     │
                                 │  SINCRONIZACIÓN  │     │
                                 └──────────────────┘     │
                                                          │
        └────────────────────────────────────────────────┘
```

## Matriz de Intersecciones (3 Filas x 5 Columnas)

```
      Columnas: a    b    c    d    e
Fila 1:  INT_1a - INT_1b - INT_1c - INT_1d - INT_1e
Fila 2:  INT_2a - INT_2b - INT_2c - INT_2d - INT_2e
Fila 3:  INT_3a - INT_3b - INT_3c - INT_3d - INT_3e
```

Cada intersección tiene **3 sensores**:
- **Cámara** (volumen de vehículos, velocidad)
- **Espira inductiva** (conteo de vehículos)
- **GPS** (velocidad promedio, nivel de congestión)

## Cronograma de Eventos de Prueba

| Tiempo (s) | Evento | Ubicación | Acción Esperada |
|-----------|--------|-----------|-----------------|
| 0-60 | Tráfico normal | Todas | Sensores envían datos normales |
| **60** | **Congestión** | **INT_2b (fila 2, col b)** | Semáforo en verde extendido |
| 60-95 | Congestión persistente | INT_2b | Mantiene verde extendido |
| **95** | **Congestión** | **INT_3d (fila 3, col d)** | Semáforo en verde extendido |
| **130** | **Ambulancia 1** | **Fila 1 completa** | Verde prioritario en INT_1a/b/c/d/e |
| **140** | **FALLO BD PRINCIPAL** | **PC3** | Cambia a BD réplica en PC2 |
| **150** | **Ambulancia 2** | **Fila 1 completa** | Verde prioritario en INT_1a/b/c/d/e |
| Continuo | **Consultas** | **PC3→PC2** | Respuestas desde servicio de analítica |

## Componentes y Puertos ZMQ

### PC1: Broker ZMQ
- **Archivo**: `PC_1/broker_mq.py`
- **Puerto SUB**: 5556 (recibe de sensores)
- **Puerto PUB**: 5557 (publica a suscriptores)
- **Función**: Retransmite eventos de sensores a servicios de analítica

### PC2: Servicios de Control

#### Servicio de Analítica (`PC_2/analisis.py`)
- **Puerto SUB**: 5557 (del broker)
- **Puerto PUSH DB**: 5558 (hacia BD principal en PC3)
- **Puerto PUSH DB Réplica**: 5560 (hacia BD réplica local)
- **Puerto PUSH Semáforos**: 5559 (hacia control de semáforos)
- **Puerto PULL Consultas**: 5561 (de PC3)
- **Función**: 
  - Suscribirse a eventos de sensores y ambulancias
  - Analizar datos y detectar congestiones
  - Enviar comandos a semáforos
  - Guardar datos en BD
  - Procesar consultas desde PC3
  - Cambiar a BD réplica si PC3 falla

#### Control de Semáforos (`PC_2/control_semaforos.py`)
- **Puerto PULL**: 5559 (de analítica)
- **Función**:
  - Recibir comandos de control de semáforos
  - Cambiar estado (ROJO/VERDE/VERDE_EXTENDIDO/VERDE_AMBULANCIA)
  - Imprimir operaciones en tiempo real

#### Base de Datos Réplica (`PC_2/db_replica.py`)
- **Puerto PULL**: 5560 (de analítica)
- **Archivo de datos**: `PC_2/db_replica.json`
- **Función**:
  - Guardar copia de todos los eventos
  - Servir como backup cuando BD principal falla
  - Activarse automáticamente a los 140s

### PC3: Consultas y Base de Datos

#### Base de Datos Principal (`PC_3/db.py`)
- **Puerto PULL**: 5558 (de analítica en PC2)
- **Archivo de datos**: `PC_3/db.json`
- **Fallo Simulado**: A los 140 segundos
- **Función**:
  - Guardar eventos de sensores
  - Simular fallo del sistema después de 140s
  - Dejar de aceptar datos tras fallo

#### Módulo de Consultas (`PC_3/consultas.py`)
- **Puerto PUSH**: 5561 (hacia analítica en PC2)
- **Función**:
  - Enviar consultas periódicas (estado general, congestiones)
  - Enviar comandos directos de usuario al servicio de analítica
  - Ejemplo: Cambiar semáforo manualmente en t=80s

## Reglas de Detección de Congestión

### Cámara
- **CONGESTIÓN**: volumen > 8 vehículos O velocidad < 15 km/h

### Espira Inductiva
- **CONGESTIÓN**: vehiculos_contados > 15

### GPS
- **CONGESTIÓN**: velocidad_promedio < 10 km/h

## Acciones Automáticas

### Ante Congestión
- **Acción**: EXTENDER_VERDE (verde normal + 10s extra)
- **Destino**: Semáforo en la intersección congestionada

### Ante Ambulancia
- **Acción**: VERDE_AMBULANCIA (prioritario)
- **Destino**: Todos los semáforos en la fila solicitante
- **Duración**: Máxima prioridad hasta que pase la emergencia

### Ante Fallo de BD Principal (t=140s)
- **Acción**: Cambiar a DB_REPLICA_PUSH_ADDRESS
- **Reporte**: "BD PRINCIPAL OFFLINE - Usando BD RÉPLICA"

## Instalación y Dependencias

### Requisitos
- Python 3.7 o superior
- ZeroMQ (libzmq)
- pyzmq

### Instalación

```bash
# Instalar ZeroMQ
# Windows (con choco):
choco install zeromq

# Linux (Ubuntu/Debian):
sudo apt-get install libzmq3-dev

# macOS (con brew):
brew install zeromq

# Instalar pyzmq
pip install pyzmq
```

## Ejecución del Sistema de Prueba

### Opción 1: Script Automatizado (Recomendado)

#### En Windows:
```bash
.\run_test.ps1
```

#### En Linux/Mac:
```bash
python run_test.py
```

### Opción 2: Manual (7 terminales)

**Terminal 1 - PC1: Broker**
```bash
cd PC_1
python broker_mq.py
```

**Terminal 2 - PC2: Semáforos**
```bash
cd PC_2
python control_semaforos.py
```

**Terminal 3 - PC2: BD Réplica**
```bash
cd PC_2
python db_replica.py
```

**Terminal 4 - PC3: BD Principal**
```bash
cd PC_3
python db.py
```

**Terminal 5 - PC2: Analítica**
```bash
cd PC_2
python analisis.py
```

**Terminal 6 - PC3: Consultas**
```bash
cd PC_3
python consultas.py
```

**Terminal 7 - ROOT: Sensores (ÚLTIMA)**
```bash
python sensores.py
```

Iniciar sensores al final, ya que eso empieza cronograma de eventos.

## Salida Esperada

### Congestión (t=60s)
```
[60.1s] [ANALÍTICA] ⚠️  CONGESTIÓN detectada en INT_2b
[60.1s] [SEMÁFOROS] 🚦 Comando para INT_2b:
[60.1s]    ✓ Estado: VERDE_EXTENDIDO (15s + 10s extra)
```

### Ambulancia (t=130s)
```
[130.2s] [ANALÍTICA] 🚑 AMBULANCIA DETECTADA A LOS 130.2s
[130.2s]    Fila: 1
[130.2s]    Acción: VERDE PRIORITARIO en intersecciones de Fila 1
[130.2s] [SEMÁFOROS] 🚦 Comando para INT_1a:
[130.2s]    ✓ Estado: VERDE PRIORITARIO (AMBULANCIA)
```

### Fallo de BD (t=140s)
```
[140.0s] ⚠️  FALLO DE BD PRINCIPAL EN PC3 DETECTADO
[140.0s] 🔄 Cambiando a BD RÉPLICA en PC2

[140.0s] 🔴 FALLO DE BD PRINCIPAL EN PC3 - 140s alcanzado
[140.0s] 🔄 BD PRINCIPAL OFFLINE - Usando BD RÉPLICA en PC2
```

### Consultas desde PC3 (t=30s, 45s, 80s)
```
[30.0s] [CONSULTAS] ✓ Consulta enviada: estado_general
[45.0s] [CONSULTAS] ✓ Consulta enviada: eventos_congestion
[80.0s] [CONSULTAS] 📋 Comando directo de usuario: INT_1b -> VERDE
```

## Archivos de Datos Generados

- **`PC_3/db.json`**: Eventos guardados en BD principal (vacío después de t=140s)
- **`PC_2/db_replica.json`**: Eventos guardados en BD réplica (completo, toma control a t=140s)

## Sistema de Medición de Desempeño

El sistema incluye un conjunto completo de herramientas para medir y evaluar desempeño:

### Métricas Implementadas

1. **Métrica 1: Eventos Almacenados en Bases de Datos**
   - Cuenta eventos persistidos en BD principal y réplica
   - Desglose por tipo de sensor y por intersección
   - Criterio: Mínimo 80 eventos en principal, 100+ en réplica

2. **Métrica 2: Tiempo de Reacción (Analítica → Semáforo)**
   - Latencia desde detección de congestión hasta comando ejecutado
   - Criterio: Promedio < 500ms, máximo < 2000ms
   - Estadísticas: promedio, mínimo, máximo por intersección

3. **Métrica 3: Eventos Especiales (Congestión, Ambulancias)**
   - Verificación de detección correcta en INT_2b (60s) e INT_3d (95s)
   - Verificación de prioridad de ambulancias (130s, 150s)
   - Criterio: Todos detectados y procesados correctamente

4. **Métrica 4: Tolerancia a Fallos (Fallover BD)**
   - Cambio automático a BD réplica a los 140s
   - Captura de eventos post-fallo
   - Criterio: Diferencia > 10 eventos post-fallo

### Herramientas de Medición

- **`metrics.py`**: Motor principal de cálculo de métricas
- **`event_tracker.py`**: Rastreador centralizado con timestamps precisos
- **`analyze_logs.py`**: Analizador de logs de consola
- **`run_test_with_metrics.py`**: Script automatizado con generación de reporte

### Procedimiento de Medición

```bash
# Opción 1: Automatizado (recomendado)
python run_test_with_metrics.py

# Opción 2: Manual después de ejecutar prueba
python -c "from metrics import generate_metrics_report; generate_metrics_report()"
```

### Archivos Generados por Métricas

- **`METRICS_REPORT.md`**: Reporte completo con todas las métricas
- **`events_trace.jsonl`**: Trazas de eventos con timestamps precisos
- **`LOG_ANALYSIS_REPORT.md`**: Análisis detallado de logs

### Documentación de Métricas

- **`METRICS_GUIDE.md`**: Guía detallada del sistema de medición
- **`METRICS_QUICK_START.md`**: Guía rápida para interpretación
- **`METRICS_SUMMARY.md`**: Resumen ejecutivo de resultados

### Criterios de Éxito

```
✓ ACEPTABLE si:
  - BD Principal ≥ 80 eventos
  - BD Réplica ≥ 100 eventos
  - Latencia promedio < 500ms
  - Congestión detectada en INT_2b y INT_3d
  - Ambulancias priorizadas correctamente
  - Fallover BD automático sin pérdida
  - Todos los criterios en checklist: OK
```

## Validaciones de Prueba

- [x] **Matriz de intersecciones**: 3x5 correctamente configurada
- [x] **3 sensores por intersección**: Cámara, Espira, GPS
- [x] **Detección de congestión**: INT_2b (t=60s), INT_3d (t=95s)
- [x] **Prioridad de ambulancias**: Fila 1 (t=130s, t=150s)
- [x] **Fallover de BD**: Cambio a réplica a t=140s
- [x] **Consultas en tiempo real**: PC3→PC2 cada 30/45s
- [x] **Comunicación asíncrona**: ZeroMQ PUB/SUB y PUSH/PULL
- [x] **Logs con timestamp**: Todos los eventos muestran tiempo transcurrido

## Configuración Avanzada

### Cambiar tiempos de eventos

Editar `config.py`:
```python
DB_FAILURE_TIME = 140  # Cambiar tiempo de fallo de BD
```

Editar `sensores.py` para ajustar tiempos de congestiones y ambulancias:
```python
if 60 <= elapsed <= 75:      # Congestión INT_2b (60-75s)
if 95 <= elapsed <= 110:     # Congestión INT_3d (95-110s)
if 130 <= elapsed <= 132:    # Ambulancia 1 (130-132s)
if 150 <= elapsed <= 152:    # Ambulancia 2 (150-152s)
```

### Cambiar IPs de comunicación

Editar `config.py`:
```python
PC1_IP = "192.168.1.100"  # IP de PC1 (broker)
PC2_IP = "192.168.1.101"  # IP de PC2 (servicios)
PC3_IP = "192.168.1.102"  # IP de PC3 (consultas/BD)
```

## Resolución de Problemas

### Problema: "Address already in use"
**Solución**: Un puerto ZMQ sigue ocupado. Esperar 5 minutos o cambiar números de puertos en `config.py`.

### Problema: "Connection refused"
**Solución**: Verificar que el broker (PC_1/broker_mq.py) está ejecutándose primero.

### Problema: No hay eventos de ambulancia
**Solución**: Verificar que sensores.py tiene lógica de ambulancias (buscar `if 130 <= elapsed`).

### Problema: BD principal nunca falla
**Solución**: Verificar que `DB_FAILURE_TIME = 140` en `config.py` y que `db.py` está ejecutándose.

## Notas de Diseño

1. **Asincronía**: Todo es asíncrono mediante ZeroMQ, sin bloqueos
2. **Replicación**: BD réplica se actualiza en tiempo real, lista para fallov
3. **Escalabilidad**: Fácil agregar más intersecciones o sensores
4. **Tolerancia a fallos**: El sistema continúa operando con BD réplica
5. **Logs temporales**: Todos los eventos muestran tiempo desde inicio

## Autores y Licencia

Sistema de prueba distribuido para demostración de arquitectura de tráfico con ZeroMQ.

---

**Versión**: 1.0
**Actualizado**: 2024
**Estado**: Listo para pruebas
