# run_test.ps1 - Script para ejecutar el sistema de prueba completo
# Ejecutar en PowerShell: .\run_test.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SISTEMA DE PRUEBA - TRÁFICO ZMQ" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script abrirá 7 terminales para ejecutar:"
Write-Host "1. PC1: Broker ZMQ" -ForegroundColor Yellow
Write-Host "2. PC2: Control de semáforos" -ForegroundColor Yellow
Write-Host "3. PC2: Base de datos réplica" -ForegroundColor Yellow
Write-Host "4. PC3: Base de datos principal" -ForegroundColor Yellow
Write-Host "5. PC2: Servicio de analítica" -ForegroundColor Yellow
Write-Host "6. PC3: Módulo de consultas" -ForegroundColor Yellow
Write-Host "7. ROOT: Sensores (ÚLTIMA - Aquí comienza la simulación)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Presiona Enter para comenzar..." -ForegroundColor Green
Read-Host

$rootDir = Get-Location
$workspace = $rootDir.Path

# Función para abrir una nueva terminal PowerShell
function Start-NewTerminal {
    param(
        [string]$Directory,
        [string]$Command,
        [string]$Title
    )
    
    $psCommand = "cd `"$Directory`"; $Command; Read-Host 'Presiona Enter para cerrar esta ventana'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $psCommand -WindowStyle Normal
}

Write-Host "Iniciando servicios..." -ForegroundColor Green
Write-Host ""

# 1. Broker en PC_1
Write-Host "[1/7] Iniciando Broker en PC_1..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_1" -Command "python broker_mq.py" -Title "PC1 - Broker"
Start-Sleep -Seconds 2

# 2. Control de semáforos en PC_2
Write-Host "[2/7] Iniciando Control de semáforos en PC_2..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_2" -Command "python control_semaforos.py" -Title "PC2 - Semáforos"
Start-Sleep -Seconds 2

# 3. DB Réplica en PC_2
Write-Host "[3/7] Iniciando BD Réplica en PC_2..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_2" -Command "python db_replica.py" -Title "PC2 - BD Réplica"
Start-Sleep -Seconds 2

# 4. DB Principal en PC_3
Write-Host "[4/7] Iniciando BD Principal en PC_3..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_3" -Command "python db.py" -Title "PC3 - BD Principal"
Start-Sleep -Seconds 2

# 5. Servicio de Analítica en PC_2
Write-Host "[5/7] Iniciando Servicio de Analítica en PC_2..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_2" -Command "python analisis.py" -Title "PC2 - Analítica"
Start-Sleep -Seconds 2

# 6. Módulo de Consultas en PC_3
Write-Host "[6/7] Iniciando Módulo de Consultas en PC_3..." -ForegroundColor Cyan
Start-NewTerminal -Directory "$workspace\PC_3" -Command "python consultas.py" -Title "PC3 - Consultas"
Start-Sleep -Seconds 3

# 7. Sensores (ÚLTIMO - inicia la simulación)
Write-Host "[7/7] Iniciando Sensores (¡SIMULACIÓN COMIENZA!)..." -ForegroundColor Green
Start-NewTerminal -Directory "$workspace" -Command "python sensores.py" -Title "SENSORES - Simulación"

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✓ Todos los servicios iniciados" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cronograma de eventos:" -ForegroundColor Yellow
Write-Host "  60s  → Congestión en INT_2b" -ForegroundColor White
Write-Host "  95s  → Congestión en INT_3d" -ForegroundColor White
Write-Host "  130s → Ambulancia 1 en Fila 1" -ForegroundColor White
Write-Host "  140s → Fallo de BD Principal (PC3), BD Réplica (PC2) toma control" -ForegroundColor White
Write-Host "  150s → Ambulancia 2 en Fila 1" -ForegroundColor White
Write-Host ""
Write-Host "Observa los logs en cada terminal para ver los eventos en tiempo real." -ForegroundColor Cyan
Write-Host ""
