@echo off
echo 🚀 Starting OAuth Demo Microservices...
echo.

echo Starting Auth Service (Port 5001)...
start "Auth Service" cmd /k "cd auth-service && pip install -r requirements.txt && python app.py"

timeout /t 3 /nobreak >nul

echo Starting Resource Service (Port 5002)...
start "Resource Service" cmd /k "cd resource-service && pip install -r requirements.txt && python app.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend Service (Port 3000)...
start "Frontend Service" cmd /k "cd frontend && pip install -r requirements.txt && python app.py"

echo.
echo ✅ All services are starting up!
echo.
echo Services:
echo   🖥️  Frontend Service:  http://localhost:3000
echo   🔐 Auth Service:      http://localhost:5001
echo   📊 Resource Service:  http://localhost:5002
echo.
echo Wait a few seconds for all services to start, then open:
echo   👉 http://localhost:3000
echo.
pause
