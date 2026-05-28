# GUÍA RÁPIDA: SISTEMA DE MÉTRICAS DE DESEMPEÑO

## Inicio Rápido

### Ejecutar prueba con métricas (recomendado)
```bash
python run_test_with_metrics.py
```

### Ejecutar prueba manual y generar métricas después
```bash
# Terminal 1-7 (ver TEST_SYSTEM.md)
python sensores.py  # Última terminal

# En otra terminal cuando termine la prueba (180+ segundos):
python -c "from metrics import generate_metrics_report; generate_metrics_report()"
```

## Las 4 Métricas Clave

### 1️⃣ Eventos Almacenados (Métrica 1)

**¿Qué mide?** Cuántos eventos llegaron a las bases de datos

**Dónde verlo:**
- Archivo: `METRICS_REPORT.md` → "Métrica 1: Eventos Almacenados"
- BD Principal: `PC_3/db.json`
- BD Réplica: `PC_2/db_replica.json`

**Lo que buscar:**
```
BD Principal: ~90 eventos (falla a los 140s)
BD Réplica:  ~100+ eventos (captura todo)
Status: ✓ OK si BD Réplica > BD Principal
```

**¿Por qué importa?** Verifica que los sensores están generando datos y llegando a las BD

---

### 2️⃣ Tiempo de Reacción (Métrica 2)

**¿Qué mide?** Milisegundos entre detectar congestión y ejecutar comando

**Fórmula:**
```
Latencia = (tiempo_comando - tiempo_detección) × 1000 ms
```

**Dónde verlo:**
- Archivo: `METRICS_REPORT.md` → "Métrica 2: Criterios de Evaluación"
- Trace: `events_trace.jsonl`

**Lo que buscar:**
```
Latencia promedio: 100-300ms
Latencia máxima: < 1000ms
Status: ✓ OK si promedio < 500ms
```

**Ejemplo real:**
```
[60.1s] ANALÍTICA detecta congestión en INT_2b
[60.2s] SEMÁFOROS ejecuta comando
Latencia: 100ms ✓ Muy rápido
```

---

### 3️⃣ Eventos Especiales (Ambulancias)

**¿Qué mide?** Si ambulancias reciben prioridad máxima

**Lo que buscar en logs:**
```
[130.2s] AMBULANCIA DETECTADA
[130.2s] VERDE PRIORITARIO (AMBULANCIA)
Status: ✓ OK si hay VERDE PRIORITARIO
```

---

### 4️⃣ Fallover de Base de Datos

**¿Qué mide?** Si el sistema cambia a BD réplica cuando falla la principal

**Lo que buscar:**
```
[140.0s] FALLO DE BD PRINCIPAL EN PC3
[140.0s] Cambiando a BD RÉPLICA en PC2

Eventos en BD Réplica post-fallo (140-180s): ✓ Capturados
Status: ✓ OK si datos no se pierden
```

---

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `METRICS_REPORT.md` | **[LEER PRIMERO]** Reporte completo con todas las métricas |
| `events_trace.jsonl` | Eventos individuales con timestamps precisos |
| `PC_3/db.json` | BD Principal (80-90 eventos) |
| `PC_2/db_replica.json` | BD Réplica (100+ eventos) |
| `analyze_logs.py` | Herramienta para analizar logs de consola |
| `metrics.py` | Motor principal de cálculo de métricas |

## Criterios de Éxito

### ✓ Sistema Operativo (Aceptable)

- [ ] BD Principal ≥ 80 eventos
- [ ] BD Réplica ≥ 100 eventos
- [ ] Latencia promedio < 500ms
- [ ] Congestión detectada en INT_2b y INT_3d
- [ ] Ambulancias priorizadas
- [ ] Fallover BD automático sin pérdida

### ⚠ Sistema Degradado (Requiere Revisión)

- [ ] BD con < 50 eventos (posible problema de sensores)
- [ ] Latencia promedio > 1000ms (problema de rendimiento)
- [ ] Congestión NO detectada (error en reglas)
- [ ] Ambulancia sin prioridad (error en procesamiento)
- [ ] Pérdida de datos post-fallo (error en fallover)

### ✗ Sistema No Funcional (Fallo)

- [ ] 0 eventos en BD (sensores o broker no funcionan)
- [ ] Latencia > 5000ms (sistema bloqueado)
- [ ] Ningún comando de semáforo ejecutado
- [ ] BD Réplica nunca activada

---

## Cómo Leer METRICS_REPORT.md

### Sección 1: Eventos Almacenados
```markdown
## Métrica 1: Eventos Almacenados

### BD Principal
- Eventos totales: 87
- Errores: 0

### BD Réplica
- Eventos totales: 108
- Errores: 0

✓ Comparación: BD Réplica es 1.24x más grande (post-fallo)
```

**Interpretación:**
- 87 en principal = OK (hasta antes de fallo)
- 108 en réplica = OK (capturó todo incluyendo post-fallo)
- Diferencia de 21 = eventos capturados después de 140s ✓

### Sección 2: Tiempos de Reacción
```markdown
### Tiempos de Reacción (Detección → Comando)

| Intersección | Count | Promedio | Mín | Máx |
|---|---|---|---|---|
| INT_2b | 12 | 95ms | 45ms | 180ms |
| INT_3d | 10 | 110ms | 62ms | 195ms |

Promedio Global: 102ms ✓
```

**Interpretación:**
- 95-110ms en promedio = Excelente
- Máximo 195ms = Dentro de límites
- Todas < 500ms = ✓ Cumple criterio

### Sección 3: Checklist
```markdown
| Criterio | Estado |
|---|---|
| Eventos llegan a analítica | **OK** |
| Congestión detectada | **OK** |
| BD Réplica activa | **OK** |
| Ambulancias prioritarias | **OK** |
| Fallover ejecutado | **OK** |
```

**Interpretación:**
- Todos OK = Sistema funcional ✓

---

## Troubleshooting Rápido

### Problema: "No hay METRICS_REPORT.md"
**Solución**: Ejecutar `generate_metrics_report()` manualmente
```bash
python -c "from metrics import generate_metrics_report; generate_metrics_report()"
```

### Problema: "0 eventos en BD"
**Verificar**:
1. ¿Broker está corriendo? `netstat -an | grep 5556`
2. ¿Sensores enviaron datos? Revisar logs de sensores
3. ¿BD escuchando? `netstat -an | grep 5558`

### Problema: "Latencia > 5000ms"
**Verificar**:
1. CPU disponible? `top` o Task Manager
2. Todas las conexiones ZMQ activas?
3. Logs de errores en consolas

### Problema: "BD Réplica igual a BD Principal"
**Verificar**:
1. ¿Sistema fue interrumpido antes de 140s?
2. ¿BD Réplica realmente activa? Revisar logs
3. ¿Timestamps correctos en config.py?

---

## Estadísticas Esperadas

### Distribución de Eventos
```
Cámara:      40% (~40 eventos)
Espira:      35% (~35 eventos)
GPS:         20% (~20 eventos)
Ambulancia:  5% (~5 eventos)
```

### Distribución de Intersecciones
```
Intersecciones con congestión (INT_2b, INT_3d): 30-40% cada una
Resto de intersecciones: distribuidos equitativamente
Fila 1 (ambulancias): picos en t=130s y t=150s
```

### Latencias Esperadas
```
Rango normal:    50-200ms
Rango aceptable: 50-500ms
Rango crítico:   500-2000ms
Rango fallo:     > 2000ms (ocurre poco)
```

---

## Comandos Útiles

### Ver eventos en BD
```bash
# Contar líneas en BD
wc -l PC_3/db.json PC_2/db_replica.json

# Ver primeros eventos
head -3 PC_3/db.json
```

### Análisis personalizado
```python
from metrics import count_events_in_file
db = count_events_in_file("PC_2/db_replica.json")
print(f"Eventos: {db['eventos_totales']}")
print(f"Tipos: {db['tipos']}")
```

### Generar trace de latencias
```python
from analyze_logs.py import LogAnalyzer
analyzer = LogAnalyzer()
# ... (cargar logs)
analyzer.generate_report()
```

---

## Contacto / Preguntas

Para más información:
- Ver `METRICS_GUIDE.md` para detalles completos
- Ver `README.md` para arquitectura del sistema
- Ver `VALIDATION.md` para checklist de requisitos

---

**Última actualización**: 2026-05-28
**Versión**: 1.0
**Estado**: ✓ Listo
