# SALIDA ESPERADA DEL SISTEMA DE PRUEBA

Este archivo muestra los logs esperados durante la ejecución del sistema de prueba.

## Terminal 1: PC1 - Broker ZMQ

```
[BROKER] Broker ZMQ activo...
[BROKER] Canales activos: camara, espira, gps, ambulancia

[BROKER] Retransmitiendo: camara {"sensor_id": "CAM-INT_1c", "tipo_sensor": "camara", ...
[BROKER] Retransmitiendo: espira {"sensor_id": "ESP-INT_2a", "tipo_sensor": "espira_inductiva", ...
[BROKER] Retransmitiendo: gps {"sensor_id": "GPS-INT_3b", "tipo_sensor": "gps", ...
```

## Terminal 2: PC2 - Control de Semáforos

```
[SEMÁFOROS] Control de semáforos activo...
[SEMÁFOROS] Tiempo verde normal: 15s

[1.2s] 🚦 Comando para INT_1b:
[1.2s]    ✓ Estado: VERDE
[1.2s]    ✓ Motivo: Tráfico normal

[60.1s] 🚦 Comando para INT_2b:
[60.1s]    ✓ Estado: VERDE_EXTENDIDO (15s + 10s extra)
[60.1s]    ✓ Motivo: Congestión detectada por camara

[95.2s] 🚦 Comando para INT_3d:
[95.2s]    ✓ Estado: VERDE_EXTENDIDO (15s + 10s extra)
[95.2s]    ✓ Motivo: Congestión detectada por espira

[130.3s] 🚦 Comando para INT_1a:
[130.3s]    ✓ Estado: VERDE PRIORITARIO (AMBULANCIA)
[130.3s]    ✓ Motivo: Ambulancia solicitando paso - Emergencia médica - Ambulancia 1

[130.3s] 🚦 Comando para INT_1b:
[130.3s]    ✓ Estado: VERDE PRIORITARIO (AMBULANCIA)
...
[150.1s] 🚦 Comando para INT_1a:
[150.1s]    ✓ Estado: VERDE PRIORITARIO (AMBULANCIA)
[150.1s]    ✓ Motivo: Ambulancia solicitando paso - Emergencia médica - Ambulancia 2
```

## Terminal 3: PC2 - Base de Datos Réplica

```
[DB RÉPLICA PC2] Base de datos réplica activa...
[DB RÉPLICA PC2] Guardando datos de eventos...

[1.1s] [DB RÉPLICA] Guardando evento: camara en INT_1c -> NORMAL
[2.5s] [DB RÉPLICA] Guardando evento: gps en INT_2a -> NORMAL
[3.8s] [DB RÉPLICA] Guardando evento: espira en INT_3d -> NORMAL

[60.2s] [DB RÉPLICA] Guardando evento: camara en INT_2b -> CONGESTION
[60.3s] [DB RÉPLICA] Guardando evento: espira en INT_2b -> CONGESTION
[60.4s] [DB RÉPLICA] Guardando evento: gps en INT_2b -> CONGESTION

[130.4s] [DB RÉPLICA] Guardando evento: ambulancia en UNKNOWN -> EMERGENCIA
[130.5s] [DB RÉPLICA] Guardando evento: ambulancia en UNKNOWN -> EMERGENCIA

[140.0s] [DB RÉPLICA] Guardando evento: camara en INT_1e -> NORMAL
[140.1s] [DB RÉPLICA] Guardando evento: espira en INT_2c -> NORMAL
```

## Terminal 4: PC3 - Base de Datos Principal

```
[DB PRINCIPAL PC3] Base de datos principal activa...
[DB PRINCIPAL PC3] Simulando fallo a los 140s...

[1.1s] [DB PRINCIPAL] Guardando evento: camara en INT_1c -> NORMAL
[2.5s] [DB PRINCIPAL] Guardando evento: gps en INT_2a -> NORMAL
[3.8s] [DB PRINCIPAL] Guardando evento: espira en INT_3d -> NORMAL

[60.2s] [DB PRINCIPAL] Guardando evento: camara en INT_2b -> CONGESTION

[130.4s] [DB PRINCIPAL] Guardando evento: ambulancia en UNKNOWN -> EMERGENCIA

[140.0s] 🔴 FALLO DE BD PRINCIPAL EN PC3 - 140s alcanzado
[140.0s] 🔄 BD PRINCIPAL OFFLINE - Usando BD RÉPLICA en PC2
```

## Terminal 5: PC2 - Servicio de Analítica

```
[ANALÍTICA] Servicio de analítica activo...
[ANALÍTICA] Esperando eventos de sensores y ambulancias...

[1.2s] Analítica procesó camara: INT_1c -> NORMAL
[2.3s] Analítica procesó espira: INT_2a -> NORMAL
[3.4s] Analítica procesó gps: INT_3b -> NORMAL

[60.1s] ⚠️  CONGESTIÓN detectada en INT_2b
[60.2s] Analítica procesó camara: INT_2b -> CONGESTION
[60.3s] Analítica procesó espira: INT_2b -> CONGESTION
[60.4s] Analítica procesó gps: INT_2b -> CONGESTION

[95.2s] ⚠️  CONGESTIÓN detectada en INT_3d
[95.3s] Analítica procesó espira: INT_3d -> CONGESTION

[130.2s] 🚑 AMBULANCIA DETECTADA A LOS 130.2s
[130.2s]    Fila: 1
[130.2s]    Motivo: Emergencia médica - Ambulancia 1
[130.2s]    Acción: VERDE PRIORITARIO en intersecciones de Fila 1

[140.0s] ⚠️  FALLO DE BD PRINCIPAL EN PC3 DETECTADO (140.0s)
[140.0s] 🔄 Cambiando a BD RÉPLICA en PC2

[150.1s] 🚑 AMBULANCIA DETECTADA A LOS 150.1s
[150.1s]    Fila: 1
[150.1s]    Motivo: Emergencia médica - Ambulancia 2
[150.1s]    Acción: VERDE PRIORITARIO en intersecciones de Fila 1
```

## Terminal 6: PC3 - Módulo de Consultas

```
[CONSULTAS PC3] Módulo de consultas activo...
[CONSULTAS PC3] Conectado al servicio de analítica en PC2

[30.0s] [CONSULTAS] ✓ Consulta enviada: estado_general
[45.0s] [CONSULTAS] ✓ Consulta enviada: eventos_congestion
[60.0s] [CONSULTAS] ✓ Consulta enviada: estado_general
[80.0s] [CONSULTAS] 📋 Comando directo de usuario: INT_1b -> VERDE
[90.0s] [CONSULTAS] ✓ Consulta enviada: estado_general
```

## Terminal 7: Sensores (ROOT)

```
[SENSORES] Iniciando simulación de ciudad 3x5...
[SENSORES] Congestión esperada en INT_2b a los 60s, INT_3d a los 95s
[SENSORES] Ambulancia fila 1 a los 130s, fila 1 a los 150s
[SENSORES] Fallo de BD en PC3 a los 140s

[1.2s] Sensor envió camara: INT_1c
[2.3s] Sensor envió gps: INT_2a
[3.4s] Sensor envió espira: INT_3d
[4.5s] Sensor envió camara: INT_1a
[5.6s] Sensor envió espira: INT_2b
[6.7s] Sensor envió gps: INT_3c

[57.8s] Sensor envió camara: INT_1b
[58.9s] Sensor envió espira: INT_2b
[59.0s] Sensor envió gps: INT_2b
[60.0s] Sensor envió camara: INT_2b
[60.1s] Sensor envió espira: INT_2b   ← COMIENZA CONGESTIÓN
[60.2s] Sensor envió gps: INT_2b      ← CONGESTIÓN DETECTADA

[92.3s] Sensor envió camara: INT_3d
[93.4s] Sensor envió espira: INT_3d
[94.5s] Sensor envió gps: INT_3d
[95.0s] Sensor envió camara: INT_3d
[95.1s] Sensor envió espira: INT_3d   ← COMIENZA CONGESTIÓN
[95.2s] Sensor envió gps: INT_3d      ← CONGESTIÓN DETECTADA

[128.7s] Sensor envió gps: INT_1d
[129.8s] Sensor envió camara: INT_1a
[129.9s] Sensor envió espira: INT_1e
[130.0s] Sensor envió gps: INT_1b
[130.1s] 🚑 AMBULANCIA SOLICITANDO PASO en Fila 1

[148.5s] Sensor envió espira: INT_1c
[149.6s] Sensor envió gps: INT_1d
[149.7s] Sensor envió camara: INT_1b
[150.0s] Sensor envió espira: INT_1a
[150.1s] 🚑 AMBULANCIA SOLICITANDO PASO en Fila 1 (2da ambulancia)

[155.2s] Sensor envió camara: INT_3a
...
```

## Archivos de Datos Generados

### PC_3/db.json (Datos hasta t=140s)
```json
{"sensor_id": "CAM-INT_1c", "tipo_sensor": "camara", "interseccion": "INT_1c", ...}
{"sensor_id": "ESP-INT_2b", "tipo_sensor": "espira_inductiva", "interseccion": "INT_2b", ...}
...
[se detiene en t=140s]
```

### PC_2/db_replica.json (Datos continuos)
```json
{"sensor_id": "CAM-INT_1c", "tipo_sensor": "camara", "interseccion": "INT_1c", ...}
{"sensor_id": "ESP-INT_2b", "tipo_sensor": "espira_inductiva", "interseccion": "INT_2b", ...}
...
[continúa recopilando datos después de t=140s]
```

## Marcas Clave a Verificar

✓ **t=60s**: Congestión en INT_2b (fila 2, columna b)
✓ **t=95s**: Congestión en INT_3d (fila 3, columna d)
✓ **t=130s**: Ambulancia 1 en fila 1 - Verde prioritario
✓ **t=140s**: BD Principal falla - Cambia a BD Réplica
✓ **t=150s**: Ambulancia 2 en fila 1 - Verde prioritario
✓ **t=30/45/60/75/90...**: Consultas desde PC3
✓ **Datos**: db.json finaliza en t=140s, db_replica.json continúa
✓ **Logs temporales**: Todos muestran tiempo transcurrido en segundos

---

**Duración total de la prueba**: ~3 minutos (180+ segundos)
