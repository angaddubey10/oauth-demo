# PowerShell script to start all microservices with configuration validation
Write-Host "🚀 Starting OAuth Demo Microservices..." -ForegroundColor Green
Write-Host ""

# Function to test configuration
function Test-Configuration {
    Write-Host "🔧 Validating configuration..." -ForegroundColor Yellow
    
    if (-not (Test-Path "config.json")) {
        Write-Host "❌ config.json not found!" -ForegroundColor Red
        Write-Host "   Please run: Copy-Item config.sample.json config.json" -ForegroundColor Yellow
        Write-Host "   Then edit config.json with your credentials" -ForegroundColor Yellow
        Write-Host "   See CONFIG_SETUP.md for detailed instructions" -ForegroundColor Yellow
        return $false
    }
    
    try {
        $config = Get-Content "config.json" | ConvertFrom-Json
        
        # Check for placeholder values
        if ($config.google_oauth.client_id -like "YOUR_*" -or $config.google_oauth.client_secret -like "YOUR_*") {
            Write-Host "⚠️  Please update config.json with your actual Google OAuth credentials" -ForegroundColor Yellow
            Write-Host "   See CONFIG_SETUP.md for instructions" -ForegroundColor Yellow
        }
        
        Write-Host "✅ Configuration validated successfully!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Invalid JSON in config.json" -ForegroundColor Red
        Write-Host "   Please check your JSON syntax" -ForegroundColor Yellow
        return $false
    }
}

# Validate configuration before starting services
if (-not (Test-Configuration)) {
    Write-Host ""
    Write-Host "Configuration validation failed. Please fix the issues above before starting services." -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor DarkGray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Function to start a service in a new PowerShell window
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [int]$Port
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Yellow
    
    $command = "cd '$Directory'; `$Host.UI.RawUI.WindowTitle = '$ServiceName'; pip install -r requirements.txt; python app.py"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    
    # Wait a moment between service starts
    Start-Sleep -Seconds 2
}

# Get the current directory
$currentDir = Get-Location

# Start Auth Service (Port 5001)
Start-Service -ServiceName "Auth Service" -Directory "$currentDir\auth-service" -Port 5001

# Start Resource Service (Port 5002)
Start-Service -ServiceName "Resource Service" -Directory "$currentDir\resource-service" -Port 5002

# Start Frontend Service (Port 3000)
Start-Service -ServiceName "Frontend Service" -Directory "$currentDir\frontend" -Port 3000

Write-Host ""
Write-Host "✅ All services are starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  🖥️  Frontend Service:  http://localhost:3000" -ForegroundColor White
Write-Host "  🔐 Auth Service:      http://localhost:5001" -ForegroundColor White
Write-Host "  📊 Resource Service:  http://localhost:5002" -ForegroundColor White
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  📄 Secrets loaded from: config.json" -ForegroundColor White
Write-Host "  🔒 config.json is excluded from git" -ForegroundColor White
Write-Host ""
Write-Host "Wait a few seconds for all services to start, then open:" -ForegroundColor Yellow
Write-Host "  👉 http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor DarkGray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
