# PowerShell script to start all microservices in debug mode
param(
    [switch]$Debug = $false,
    [switch]$VSCode = $false
)

Write-Host "🚀 Starting OAuth Demo Microservices..." -ForegroundColor Green
if ($Debug) {
    Write-Host "🐛 Debug mode enabled - services will wait for debugger attachment" -ForegroundColor Yellow
}
Write-Host ""

# Function to start a service in debug mode
function Start-ServiceDebug {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [int]$Port,
        [int]$DebugPort
    )
    
    Write-Host "Starting $ServiceName on port $Port (Debug port: $DebugPort)..." -ForegroundColor Yellow
    
    if ($VSCode) {
        # For VS Code debugging - just install requirements
        $command = "cd '$Directory'; `$Host.UI.RawUI.WindowTitle = '$ServiceName'; pip install -r requirements.txt; Write-Host 'Ready for VS Code debugger. Press F5 in VS Code to start debugging.' -ForegroundColor Green; Read-Host 'Press Enter to continue'"
    } else {
        # Use debugpy for remote debugging
        $command = "cd '$Directory'; `$Host.UI.RawUI.WindowTitle = '$ServiceName'; pip install -r requirements.txt debugpy; python -m debugpy --listen 0.0.0.0:$DebugPort --wait-for-client app.py"
    }
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    Start-Sleep -Seconds 2
}

# Function to start a service normally
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [int]$Port
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Yellow
    
    $command = "cd '$Directory'; `$Host.UI.RawUI.WindowTitle = '$ServiceName'; pip install -r requirements.txt; python app.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    Start-Sleep -Seconds 2
}

# Get the current directory
$currentDir = Get-Location

if ($Debug) {
    # Start services in debug mode with different debug ports
    Start-ServiceDebug -ServiceName "Auth Service" -Directory "$currentDir\auth-service" -Port 5001 -DebugPort 5678
    Start-ServiceDebug -ServiceName "Resource Service" -Directory "$currentDir\resource-service" -Port 5002 -DebugPort 5679
    Start-ServiceDebug -ServiceName "Frontend Service" -Directory "$currentDir\frontend" -Port 3000 -DebugPort 5680
} else {
    # Start services normally
    Start-Service -ServiceName "Auth Service" -Directory "$currentDir\auth-service" -Port 5001
    Start-Service -ServiceName "Resource Service" -Directory "$currentDir\resource-service" -Port 5002
    Start-Service -ServiceName "Frontend Service" -Directory "$currentDir\frontend" -Port 3000
}

Write-Host ""
Write-Host "✅ All services are starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  🖥️  Frontend Service:  http://localhost:3000" -ForegroundColor White
Write-Host "  🔐 Auth Service:      http://localhost:5001" -ForegroundColor White
Write-Host "  📊 Resource Service:  http://localhost:5002" -ForegroundColor White

if ($Debug -and -not $VSCode) {
    Write-Host ""
    Write-Host "Debug ports:" -ForegroundColor Cyan
    Write-Host "  🐛 Auth Service Debug:      localhost:5678" -ForegroundColor White
    Write-Host "  🐛 Resource Service Debug:  localhost:5679" -ForegroundColor White
    Write-Host "  🐛 Frontend Service Debug:  localhost:5680" -ForegroundColor White
    Write-Host ""
    Write-Host "Attach your debugger to these ports to start debugging!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Wait a few seconds for all services to start, then open:" -ForegroundColor Yellow
Write-Host "  👉 http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
