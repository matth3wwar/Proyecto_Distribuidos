# GUÍA DE TROUBLESHOOTING - Sistema de Métricas

## Tabla de Síntomas y Soluciones

| Síntoma | Causa Probable | Verificar | Solución |
|---------|---|---|---|
| 0 eventos en BD | Broker no inicia | Verificar puerto 5556 | Ver: Problema #1 |
| Eventos sólo en BD Réplica | BD Principal no recibe | Verificar puerto 5558 | Ver: Problema #2 |
| Latencia > 5000ms | Sistema bloqueado | CPU/RAM disponible | Ver: Problema #3 |
| Congestión no detectada | Evento no llegó | Revisar sensores | Ver: Problema #4 |
| Ambulancia sin prioridad | Regla no aplicada | Revisar analítica | Ver: Problema #5 |
| BD Réplica igual a Principal | Prueba interrumpida | Tiempo de ejecución | Ver: Problema #6 |

---

## Problema #1: Broker No Inicia / 0 Eventos

### Síntomas
```
[ERROR] No se puede conectar a broker
[ERROR] No hay eventos en bd.json
[ERROR] Puerto 5556 en uso
```

### Verificación

```bash
# 1. ¿Puerto está libre?
netstat -an | grep 5556
# Si muestra línea: puerto está en uso

# 2. ¿Proceso anterior activo?
ps aux | grep broker
# Si muestra proceso: matar con kill

# 3. ¿Python disponible?
python --version
# Debe ser Python 3.8+

# 4. ¿zmq instalado?
python -c "import zmq; print(zmq.zmq_version())"
# Debe mostrar versión
```

### Soluciones

**Opción A: Liberar puerto**
```bash
# Windows
netstat -ano | findstr :5556
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5556 | xargs kill -9
```

**Opción B: Instalar dependencias**
```bash
pip install pyzmq
```

**Opción C: Cambiar puerto**
```python
# En config.py
BROKER_BIND_ADDRESS = "tcp://127.0.0.1:5557"  # Cambiar a puerto libre
```

### Verificación Post-Solución
```bash
# Ejecutar broker solo
python PC_1/broker_mq.py

# En otra terminal
python -c "import zmq; s = zmq.Context().socket(zmq.PUB); s.connect('tcp://127.0.0.1:5556'); print('OK')"
```

---

## Problema #2: BD Principal No Recibe Eventos

### Síntomas
```
db.json está vacío (0 bytes)
db_replica.json tiene eventos
ANALÍTICA dice: evento guardado (pero db.json no crece)
```

### Verificación

```bash
# 1. ¿Puerto 5558 abierto?
netstat -an | grep 5558

# 2. ¿db.py está corriendo?
ps aux | grep db.py

# 3. ¿Hay errores en PC_3?
# Revisar terminal donde corre db.py

# 4. ¿config.py correcto?
python -c "from config import DB_BIND_ADDRESS; print(DB_BIND_ADDRESS)"
# Debe ser: tcp://127.0.0.1:5558
```

### Causas Comunes

```
A. BD PRINCIPAL NO INICIA
   Solución: Verificar puerto 5558, instalar zmq

B. ANALÍTICA NO ENVÍA A PUERTO CORRECTO
   Solución: Verificar config.py - DB_PUSH_ADDRESS

C. BD.PY NO GUARDA EVENTOS
   Solución: Verificar permisos en directorio PC_3
   
D. EVENTO LLEGA DESPUÉS DE FALLO
   Solución: Fallo a los 140s es normal, esperado
```

### Verificación Post-Solución

```bash
# Terminal 1: Ejecutar DB
python PC_3/db.py

# Terminal 2: Enviar evento de prueba
python -c "
import zmq
ctx = zmq.Context()
socket = ctx.socket(zmq.PUSH)
socket.connect('tcp://127.0.0.1:5558')
socket.send_json({'test': 'data'})
"

# Terminal 1 debe mostrar: evento recibido
# Archivo PC_3/db.json debe crecer
```

---

## Problema #3: Latencia Alta (>5000ms)

### Síntomas
```
METRICS_REPORT.md muestra:
  Latencia promedio: 8000ms ✗
  Latencia máxima: 15000ms ✗
Todos los comandos se ejecutan muy lentamente
```

### Verificación

```bash
# 1. ¿CPU disponible?
# Windows: Task Manager > CPU
# Linux: top

# 2. ¿Memoria disponible?
# Windows: Task Manager > Memory
# Linux: free -h

# 3. ¿Procesos bloqueados?
ps aux | grep python
# Muchos procesos = problema

# 4. ¿Red funcionando?
ping 127.0.0.1
# Debe responder inmediatamente

# 5. ¿Logs muestran errores?
# Revisar todas las terminales de servicios
```

### Causas Comunes

```
A. CPU SATURADA (>90%)
   Solución:
   - Cerrar otras aplicaciones
   - Usar máquina con más recursos
   - Reducir carga de sensores

B. MEMORIA INSUFICIENTE
   Solución:
   - Cerrar navegadores/aplicaciones
   - Ejecutar en máquina diferente
   - Aumentar RAM

C. FIREWALL BLOQUEANDO
   Solución:
   - Desactivar firewall temporalmente
   - Permitir Python en firewall
   - Usar localhost (127.0.0.1)

D. SOCKET NO CONFIGURADO CORRECTAMENTE
   Solución:
   - Verificar config.py
   - Revisar all BIND/CONNECT addresses
   - Usar puerto local (localhost)
```

### Verificación Post-Solución

```bash
# Monitorear latencia en tiempo real
while true; do
  tail -1 events_trace.jsonl
  sleep 1
done

# Debe mostrar eventos ~100ms de diferencia entre detección y comando
```

---

## Problema #4: Congestión No Se Detecta

### Síntomas
```
Logs no muestran:
  [60.1s] CONGESTION detectada en INT_2b
  [95.1s] CONGESTION detectada en INT_3d
db.json no tiene eventos de congestión
```

### Verificación

```bash
# 1. ¿Sensores generan eventos?
python sensores.py
# Verificar que muestra eventos

# 2. ¿Eventos llegan a broker?
# Buscar en logs de broker_mq.py:
#   - eventos recibidos
#   - eventos reenviados

# 3. ¿Analítica procesa?
# Buscar en logs de analisis.py:
#   - eventos analizados
#   - reglas aplicadas

# 4. ¿Valores de congestión correctos?
grep -i "congestion" config.py
# Debe mostrar umbrales:
#   CAMERA: volumen > 8 OR velocidad < 15
#   ESPIRA: vehiculos > 15
#   GPS: velocidad < 10
```

### Causas Comunes

```
A. SENSORES NO GENERAN CONGESTIÓN
   Solución:
   - Verificar tiempo de ejecución
   - Revisar sensores.py línea de congestión
   - Asegurar elapsed_time correcto

B. EVENTO NO LLEGA A ANALÍTICA
   Solución:
   - Verificar broker está corriendo
   - Verificar puerto 5557
   - Revisar logs de broker

C. REGLAS DE DETECCIÓN INCORRECTAS
   Solución:
   - Revisar evaluar_sensor() en analisis.py
   - Verificar umbrales en config.py
   - Probar con valores fijos para debug

D. ANALÍTICA NO ENVÍA COMANDO
   Solución:
   - Revisar puerto 5559 (semáforos)
   - Verificar PUSH socket en analítica
   - Revisar logs de semáforos
```

### Verificación Post-Solución

```bash
# Test de regla de congestión
python -c "
evento = {
    'tipo_sensor': 'camara',
    'volumen': 10,  # > 8 (congestión)
    'velocidad': 5  # < 15 (congestión)
}
# Debería detectar congestión
"

# Verificar que logs muestran: CONGESTION detectada
```

---

## Problema #5: Ambulancia Sin Prioridad

### Síntomas
```
[130.2s] AMBULANCIA DETECTADA
[130.2s] Pero NO hay VERDE PRIORITARIO
Semáforos mostran VERDE_EXTENDIDO en lugar de VERDE PRIORITARIO
```

### Verificación

```bash
# 1. ¿Ambulancia fue generada?
# Buscar en logs de sensores:
#   [130.0s] Generando ambulancia

# 2. ¿Analítica recibió?
# Buscar en logs de analisis.py:
#   AMBULANCIA DETECTADA

# 3. ¿Comando fue enviado?
# Buscar en logs de semáforos:
#   VERDE PRIORITARIO

# 4. ¿Evento almacenado?
grep -i "ambulancia" PC_2/db_replica.json
```

### Causas Comunes

```
A. AMBULANCIA NO GENERADA EN TIEMPO CORRECTO
   Solución:
   - Verificar AMBULANCIA1_TIME y AMBULANCIA2_TIME en config.py
   - Deben ser: 130 y 150 segundos

B. TIPO DE EVENTO INCORRECTO
   Solución:
   - Verificar en sensores.py: generate_ambulance_event()
   - Debe enviar: tipo="ambulancia"

C. REGLA DE PRIORIDAD NO SE APLICA
   Solución:
   - Revisar analisis.py: buscar "ambulancia"
   - Debe aplicar acción VERDE_AMBULANCIA

D. COMANDO NO LLEGA A SEMÁFOROS
   Solución:
   - Verificar puerto 5559
   - Revisar PUSH socket en analítica
```

### Verificación Post-Solución

```bash
# Verificar evento ambulancia en BD
python -c "
import json
with open('PC_2/db_replica.json') as f:
    for line in f:
        event = json.loads(line)
        if 'ambulancia' in str(event).lower():
            print(event)
"

# Debe mostrar: "tipo_sensor": "ambulancia" o similar
# Y/O "estado": "AMBULANCIA"
```

---

## Problema #6: BD Réplica Igual a BD Principal

### Síntomas
```
count_events: BD Principal = 87
count_events: BD Réplica = 87 (IGUAL!)
Esperado: BD Réplica > BD Principal
No hay diferencia post-fallo (140s+)
```

### Verificación

```bash
# 1. ¿Duración de prueba?
# Debe ejecutar mínimo 185 segundos
# Si menos: prueba interrumpida

# 2. ¿Tiempo de fallo correcto?
grep "DB_FAILURE_TIME" config.py
# Debe ser: 140

# 3. ¿Cambio activado?
# Buscar en logs de analisis.py:
#   [140.0s] FALLO DE BD - Cambiando a BD RÉPLICA

# 4. ¿Eventos post-140s?
# Verificar últimos eventos en db_replica.json:
tail -10 PC_2/db_replica.json
# Debe haber eventos con timestamp > 140
```

### Causas Comunes

```
A. PRUEBA EJECUTADA MENOS DE 140 SEGUNDOS
   Solución:
   - Verificar duración en config.py
   - Cambiar: PRUEBA_DURACION = 185
   - Ejecutar de nuevo

B. CAMBIO NO SE ACTIVÓ EN ANALÍTICA
   Solución:
   - Revisar analisis.py: global db_primary_active
   - Verificar línea: if get_elapsed_time() >= DB_FAILURE_TIME
   - Debe cambiar socket a db_replica

C. BD RÉPLICA NO RECIBE POST-FALLO
   Solución:
   - Verificar puerto 5560 en config
   - Revisar db_replica.py: está escuchando?
   - Verificar logs de db_replica.py

D. TIMESTAMP INCORRECTO EN EVENTOS
   Solución:
   - Verificar get_elapsed_time() en sensores
   - Debe contar segundos desde inicio
   - No usar time.time() sino elapsed desde START
```

### Verificación Post-Solución

```bash
# Analizar timeline de eventos
python -c "
import json
print('Últimos 5 eventos:')
with open('PC_2/db_replica.json') as f:
    lines = f.readlines()
    for line in lines[-5:]:
        event = json.loads(line)
        elapsed = event.get('elapsed_seconds', event.get('time', '?'))
        print(f'  t={elapsed}s: {event.get(\"tipo_sensor\", \"?\")}')"

# Debe mostrar eventos en rango 140-180+ segundos
```

---

## Problema #7: METRICS_REPORT.md No Se Genera

### Síntomas
```
Ejecutar: python run_test_with_metrics.py
No se crea archivo: METRICS_REPORT.md
Error en consola o sin mensaje
```

### Verificación

```bash
# 1. ¿Prueba ejecutó completamente?
# Script debe llegar al final (185+ segundos)

# 2. ¿Archivos db.json existen?
ls -l PC_3/db.json PC_2/db_replica.json

# 3. ¿Archivo es válido JSON?
python -c "
import json
with open('PC_2/db_replica.json') as f:
    for i, line in enumerate(f):
        try:
            json.loads(line)
        except:
            print(f'Error en línea {i}: {line}')
"

# 4. ¿Permisos de escritura?
touch METRICS_REPORT.md  # Probar crear archivo
```

### Causas Comunes

```
A. PRUEBA INTERRUMPIDA
   Solución:
   - Ejecutar nuevamente: python run_test_with_metrics.py
   - NO interrumpir (Ctrl+C) antes de 185s

B. ARCHIVO BD NO VÁLIDO
   Solución:
   - Limpiar archivos: rm PC_*/db*.json
   - Ejecutar de nuevo

C. PERMISOS INSUFICIENTES
   Solución:
   - Verificar directorio está escribible
   - Cambiar permisos: chmod 755 .

D. BUG EN metrics.py
   Solución:
   - Verificar sintaxis: python -m py_compile metrics.py
   - Revisar imports en metrics.py
```

### Verificación Post-Solución

```bash
# Generar reporte manualmente
python -c "
from metrics import generate_metrics_report
print('Generando reporte...')
resultado = generate_metrics_report()
print('✓ Reporte generado')
"

# Verificar archivo
cat METRICS_REPORT.md | head -20
```

---

## Problema #8: Logs Confusos o Incompletos

### Síntomas
```
Logs no muestran eventos esperados
Componentes no se ven coordinados
No queda claro qué pasó en cada momento
```

### Solución: Capturar y Guardar Logs

```bash
# Windows - Ejecutar en PowerShell
$date = (Get-Date -Format "yyyyMMdd_HHmmss")
python PC_1/broker_mq.py 2>&1 | Tee-Object -FilePath "log_broker_$date.txt"
python PC_2/analisis.py 2>&1 | Tee-Object -FilePath "log_analisis_$date.txt"
# ... etc para cada terminal

# Linux/Mac
date_str=$(date +%Y%m%d_%H%M%S)
python PC_1/broker_mq.py 2>&1 | tee log_broker_$date_str.txt
python PC_2/analisis.py 2>&1 | tee log_analisis_$date_str.txt
# ... etc
```

### Analizar Logs Guardados

```bash
# Buscar errores
grep -i "error" log_*.txt

# Buscar congestión
grep -i "congestion" log_*.txt

# Buscar timestamps
grep "\[.*s\]" log_*.txt | sort

# Generar reporte de logs
python analyze_logs.py < log_analisis_*.txt
```

---

## Problema #9: Variabilidad en Métricas (Resultados No Consistentes)

### Síntomas
```
Primera ejecución: Latencia 100ms
Segunda ejecución: Latencia 500ms
Diferentes resultados cada vez
```

### Causas Comunes

```
A. VARIACIÓN POR CARGA DEL SISTEMA
   Solución:
   - Cerrar otras aplicaciones
   - Ejecutar en ambiente aislado
   - Repetir 3 veces y promediar

B. SINCRONIZACIÓN DE TIEMPO INCORRECTA
   Solución:
   - Verificar reloj del sistema
   - Usar NTP: ntpdate -s time.nist.gov
   - Revisar get_elapsed_time()

C. EVENTOS GENERADOS CON VARIABILIDAD
   Solución:
   - Revisar SENSOR_INTERVAL en config.py
   - Debe ser fijo (no random)
   - Eventos a tiempos determinísticos

D. PROCESAMIENTO ASINCRÓNICO
   Solución:
   - Esperado en sistemas distribuidos
   - Medir en múltiples ejecuciones
   - Reportar promedio ± desviación
```

### Verificación Post-Solución

```bash
# Ejecutar 3 veces y comparar
for i in {1..3}; do
  echo "Ejecución $i:"
  python run_test_with_metrics.py
  grep "Promedio" METRICS_REPORT.md | tail -1
done

# Resultado debe ser similar ±10%
```

---

## Árbol de Decisión Rápido

```
¿Qué falla?
│
├─ Broker no inicia
│  └─ Ver: Problema #1
│
├─ 0 eventos en BD
│  ├─ BD Principal vacío → Problema #2
│  ├─ BD Réplica vacío → Problema #3 o #2
│  └─ Ambos vacíos → Problema #1
│
├─ Latencia muy alta
│  └─ Ver: Problema #3
│
├─ Congestión no detectada
│  └─ Ver: Problema #4
│
├─ Ambulancia sin prioridad
│  └─ Ver: Problema #5
│
├─ BD Réplica igual a Principal
│  └─ Ver: Problema #6
│
├─ METRICS_REPORT.md no existe
│  └─ Ver: Problema #7
│
└─ Logs confusos
   └─ Ver: Problema #8
```

---

## Checklist de Resolución

Después de intentar solucionar:

```
☐ Problema identificado claramente
☐ Causa probable identificada
☐ Solución aplicada
☐ Sistema reiniciado
☐ Prueba ejecutada nuevamente
☐ Verificación exitosa
☐ Logs guardados para referencia
☐ Documentado cambio realizado
```

---

## Contacto / Escalado

Si después de estas soluciones el problema persiste:

1. **Guardar toda la información**:
   - Logs completos (7 archivos)
   - METRICS_REPORT.md
   - events_trace.jsonl
   - Versión de Python: `python --version`
   - Versión zmq: `python -c "import zmq; print(zmq.zmq_version())"`

2. **Verificar requisitos mínimos**:
   - Python 3.8+
   - ZeroMQ 4.0+
   - 2GB RAM disponible
   - CPU > 50% disponible

3. **Considerar ambiente alternativo**:
   - Ejecutar en máquina diferente
   - Usar container Docker
   - Aumentar recursos del sistema

---

**Versión**: 1.0  
**Estado**: ✓ Completo  
**Última actualización**: 2026-05-28

*Para más información ver: README.md, TEST_SYSTEM.md, METRICS_GUIDE.md*
