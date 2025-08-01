# OAuth Demo - Microservices Architecture

This project demonstrates a microservices architecture with OAuth authentication using Google OAuth 2.0.

## Architecture Overview

The application is split into three separate services:

### 1. Frontend Service (Port 3000)
- **Location**: `frontend/`
- **Purpose**: Serves the web UI and handles user interactions
- **Technology**: Flask with HTML templates
- **Responsibilities**: User interface, session management, API coordination

### 2. Auth Service (Port 5001)
- **Location**: `auth-service/`  
- **Purpose**: Handles authentication and JWT token management
- **Technology**: Flask with Google OAuth 2.0
- **Responsibilities**: OAuth integration, JWT tokens, user roles

### 3. Resource Service (Port 5002)
- **Location**: `resource-service/`
- **Purpose**: Manages protected resources with role-based access control  
- **Technology**: Flask with JWT verification
- **Responsibilities**: Resource data, access control, API endpoints

## Quick Start

### Prerequisites
- Python 3.7+
- Google OAuth 2.0 credentials (see [CONFIG_SETUP.md](CONFIG_SETUP.md))

### Setup Configuration
Before running the application, set up your configuration file:

1. **Copy the sample configuration:**
   ```powershell
   Copy-Item config.sample.json config.json
   ```

2. **Edit `config.json` with your Google OAuth credentials:**
   - Get credentials from [Google Cloud Console](https://console.cloud.google.com/)
   - Update `client_id` and `client_secret` in the config file
   - See [CONFIG_SETUP.md](CONFIG_SETUP.md) for detailed instructions

### Option 1: Start All Services (Recommended)
```powershell
# Windows PowerShell
.\start-all-services.ps1

# Or Command Prompt  
start-all-services.bat
```

### Option 2: Start Services Individually

**Terminal 1 - Auth Service:**
```powershell
cd auth-service
pip install -r requirements.txt
python app.py
```

**Terminal 2 - Resource Service:**
```powershell
cd resource-service  
pip install -r requirements.txt
python app.py
```

**Terminal 3 - Frontend Service:**
```powershell
cd frontend
pip install -r requirements.txt  
python app.py
```

## Usage

1. Open browser: http://localhost:3000
2. Click "Sign in with Google"
3. Complete OAuth flow
4. Explore dashboard based on your role

## Service Communication

```
Browser → Frontend (3000) → Auth Service (5001) ← Google OAuth
              ↓
         Resource Service (5002)
```

## User Roles

- **Regular User**: Access to user resources and profile
- **Admin User**: Access to all resources plus admin functions

**To become admin:** Edit `USER_ROLES` in `auth-service/app.py` and add your email.

## API Endpoints

### Auth Service (5001)
- `GET /health` - Health check
- `GET /auth/login` - Start OAuth flow
- `POST /auth/verify` - Verify JWT token

### Resource Service (5002)
- `GET /health` - Health check  
- `GET /resources/user` - User resources
- `GET /resources/admin` - Admin resources (admin only)
- `GET /user/profile` - User profile
- `GET /admin/stats` - System stats (admin only)

### Frontend Service (3000)
- `GET /` - Home page
- `GET /dashboard` - Main dashboard
- `GET /logout` - Logout

## Configuration

Configuration is now managed through a `config.json` file that contains all secrets and settings. This file is excluded from git for security.

**Setup Steps:**
1. Copy `config.sample.json` to `config.json`
2. Update with your Google OAuth credentials
3. Customize other settings as needed

See [CONFIG_SETUP.md](CONFIG_SETUP.md) for detailed configuration instructions.

## Project Structure

```
oauth-demo/
├── config.json              # Configuration file (excluded from git)
├── config.sample.json       # Sample configuration template
├── .gitignore               # Git ignore rules
├── CONFIG_SETUP.md          # Configuration setup guide
├── frontend/
│   ├── app.py
│   ├── templates/
│   └── requirements.txt
├── auth-service/
│   ├── app.py  
│   └── requirements.txt
├── resource-service/
│   ├── app.py
│   └── requirements.txt
├── start-all-services.ps1
├── start-all-services.bat
└── README.md
```

## Troubleshooting

**Services won't start:**
- Check ports 3000, 5001, 5002 are free
- Install dependencies: `pip install -r requirements.txt`

**Login issues:**
- Check browser console for errors
- Verify Google OAuth credentials
- Clear browser cache/cookies

**CORS errors:**
- All services have CORS enabled
- Check service URLs in frontend app.py

## Security Notes

**Configuration Security:**
- All secrets are now stored in `config.json` (excluded from git)
- Use environment variables for production deployments
- Regularly rotate your OAuth credentials and secret keys

**For production use:**
- Never commit `config.json` to version control
- Use environment variables or secure secret management  
- Add HTTPS
- Add rate limiting
- Implement proper logging

---

🚀 **Ready to start?** 

1. **Set up configuration:** Copy `config.sample.json` to `config.json` and update with your credentials
2. **Start services:** Run `.\start-all-services-secure.ps1` (validates configuration first)
3. **Open application:** Visit http://localhost:3000

See [CONFIG_SETUP.md](CONFIG_SETUP.md) for detailed setup instructions.
