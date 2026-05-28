# SISTEMA DE PRUEBA - DISTRIBUCIÓN DE TRÁFICO CON ZEROMQ

## Descripción del sistema de prueba

Este sistema simula una ciudad de 3 filas x 5 columnas con:
- **Matriz de intersecciones**: 1a-1e, 2a-2e, 3a-3e (15 intersecciones total)
- **3 sensores por intersección**: cámara, espira inductiva, GPS
- **Comunicación**: ZeroMQ (PUB/SUB, PUSH/PULL)

## Cronograma de eventos de prueba

| Tiempo (s) | Evento | Ubicación | Descripción |
|-----------|--------|-----------|-------------|
| 60 | Congestión | INT_2b | Tráfico congestionado detectado |
| 95 | Congestión | INT_3d | Segunda congestión |
| 130 | Ambulancia 1 | Fila 1 | Primera ambulancia solicita paso |
| 140 | Fallo BD | PC3 | BD principal cae, BD réplica en PC2 toma control |
| 150 | Ambulancia 2 | Fila 1 | Segunda ambulancia solicita paso |
| Continuo | Consultas | PC3→PC2 | Consultas desde PC3 al servicio de analítica |

## Arquitectura

```
PC1: Broker ZMQ
├── PUB/SUB: Recibe eventos de sensores
└── Retransmite a servicios de analítica

PC2: Servicios de Control
├── analisis.py: Procesa eventos y detecta anomalías
├── control_semaforos.py: Ejecuta cambios de semáforos
└── db_replica.py: Base de datos réplica (backup)

PC3: Consultas y BD Principal
├── db.py: Base de datos principal (cae a los 140s)
└── consultas.py: Módulo para hacer consultas a PC2
```

## Instrucciones de ejecución

### 1. Terminal 1 - PC1: Broker ZMQ
```bash
cd PC_1
python broker_mq.py
```
**Esperado**: 
```
[BROKER] Broker ZMQ activo...
[BROKER] Retransmitiendo: ...
```

### 2. Terminal 2 - PC2: Control de semáforos
```bash
cd PC_2
python control_semaforos.py
```
**Esperado**:
```
[SEMÁFOROS] Control de semáforos activo...
```

### 3. Terminal 3 - PC2: Base de datos réplica
```bash
cd PC_2
python db_replica.py
```
**Esperado**:
```
[DB RÉPLICA PC2] Base de datos réplica activa...
```

### 4. Terminal 4 - PC3: Base de datos principal
```bash
cd PC_3
python db.py
```
**Esperado**:
```
[DB PRINCIPAL PC3] Base de datos principal activa...
[DB PRINCIPAL PC3] Simulando fallo a los 140s...
```

### 5. Terminal 5 - PC2: Servicio de analítica
```bash
cd PC_2
python analisis.py
```
**Esperado**:
```
[ANALÍTICA] Servicio de analítica activo...
```

### 6. Terminal 6 - PC3: Módulo de consultas
```bash
cd PC_3
python consultas.py
```
**Esperado**:
```
[CONSULTAS PC3] Módulo de consultas activo...
```

### 7. Terminal 7 - Sensores (ÚLTIMA)
```bash
python sensores.py
```
**Esperado**:
```
[SENSORES] Iniciando simulación de ciudad 3x5...
[SENSORES] Congestión esperada en INT_2b a los 60s, INT_3d a los 95s
[SENSORES] Ambulancia fila 1 a los 130s, fila 1 a los 150s
[SENSORES] Fallo de BD en PC3 a los 140s
```

## Eventos clave a observar

### 60 segundos - Congestión en INT_2b
```
[60.0s] [ANALÍTICA] ⚠️  CONGESTIÓN detectada en INT_2b
[60.0s] [SEMÁFOROS] 🚦 Comando para INT_2b:
[60.0s]    ✓ Estado: VERDE_EXTENDIDO
```

### 95 segundos - Congestión en INT_3d
```
[95.0s] [ANALÍTICA] ⚠️  CONGESTIÓN detectada en INT_3d
```

### 130 segundos - Primera ambulancia
```
[130.0s] [ANALÍTICA] 🚑 AMBULANCIA DETECTADA A LOS 130.0s
[130.0s]    Fila: 1
[130.0s]    Motivo: Emergencia médica - Ambulancia 1
[130.0s]    Acción: VERDE PRIORITARIO en intersecciones de Fila 1
[130.0s] [SEMÁFOROS] 🚦 Comando para INT_1a:
[130.0s]    ✓ Estado: VERDE PRIORITARIO (AMBULANCIA)
```

### 140 segundos - Fallo de BD
```
[140.0s] ⚠️  FALLO DE BD PRINCIPAL EN PC3 DETECTADO (140.0s)
[140.0s] 🔄 Cambiando a BD RÉPLICA en PC2

[140.0s] 🔴 FALLO DE BD PRINCIPAL EN PC3 - 140s alcanzado
[140.0s] 🔄 BD PRINCIPAL OFFLINE - Usando BD RÉPLICA en PC2
```

### 150 segundos - Segunda ambulancia
Similar al evento de los 130 segundos

### Consultas desde PC3
```
[30.0s] [CONSULTAS] ✓ Consulta enviada: estado_general
[45.0s] [CONSULTAS] ✓ Consulta enviada: eventos_congestion
[80.0s] [CONSULTAS] 📋 Comando directo de usuario: INT_1b -> VERDE
```

## Archivos generados

- `PC_3/db.json`: Registros de BD principal (vacío después de 140s)
- `PC_2/db_replica.json`: Registros de BD réplica (completo)

## Validaciones

✓ **Congestiones detectadas**: INT_2b en t=60s, INT_3d en t=95s
✓ **Ambulancias procesadas**: Con prioridad CRÍTICA en t=130s y t=150s
✓ **Fallo de BD**: BD principal falla a los 140s, réplica toma control
✓ **Comunicación**: Todos los servicios se comunican vía ZMQ
✓ **Logs temporales**: Todos los eventos muestran timestamp en segundos

## Dependencias

- Python 3.7+
- ZeroMQ (zmq)
- pyzmq: `pip install pyzmq`

## Notas importantes

1. **IPs**: Configuradas en config.py (127.0.0.1 para localhost)
2. **Puertos**: Ver config.py para mapeo de puertos
3. **Sincronización**: Los tiempos se cuentan desde el inicio de sensores.py
4. **Orden de ejecución**: Broker primero, luego servicios, sensores al final
5. **Limpieza**: Los archivos db.json se sobreescriben en cada ejecución
