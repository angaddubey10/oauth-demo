# Debugging OAuth Demo - Step by Step Guide

## Method 1: VS Code Integrated Debugger (Easiest)

### Setup:
1. Install the Python extension in VS Code
2. Open the project in VS Code
3. The launch configuration is already created in `.vscode/launch.json`

### Debug Individual Services:
1. Open VS Code
2. Go to Run and Debug (Ctrl+Shift+D)
3. Select one of:
   - "Debug Auth Service"
   - "Debug Frontend Service" 
   - "Debug Resource Service"
4. Press F5 to start debugging

### Debug All Services Together:
1. Select "Debug All Services" from the dropdown
2. Press F5 - this will start all three services in debug mode

### Setting Breakpoints:
1. Open any Python file (e.g., `auth-service/app.py`)
2. Click in the gutter next to line numbers to set breakpoints
3. Red dots indicate active breakpoints

### Key Places to Set Breakpoints:

#### Auth Service (`auth-service/app.py`):
- Line ~70: `/auth/login` endpoint
- Line ~100: `/auth/callback` endpoint  
- Line ~150: JWT token creation
- Line ~200: Token validation

#### Frontend Service (`frontend/app.py`):
- Line ~60: Login route
- Line ~80: Dashboard route
- Line ~120: API calls to other services

#### Resource Service (`resource-service/app.py`):
- Line ~60: Token validation decorator
- Line ~100: Protected resource endpoints

## Method 2: Remote Debugging with debugpy

### Start Services in Debug Mode:
```powershell
.\start-all-services-debug.ps1 -Debug
```

### Attach Debugger:
1. Services will wait for debugger attachment
2. In VS Code, create a new launch configuration:
```json
{
    "name": "Attach to Auth Service",
    "type": "debugpy", 
    "request": "attach",
    "connect": {
        "host": "localhost",
        "port": 5678
    }
}
```
3. Repeat for other services (ports 5679, 5680)

## Method 3: Enhanced Logging

### Enable Debug Logging:
The `debug_utils.py` file provides enhanced logging. To use it:

1. Import in your service files:
```python
from debug_utils import debug_oauth_flow, log_request_details
```

2. Add decorators to functions you want to trace:
```python
@debug_oauth_flow
def login():
    # your code here
```

3. Check the `oauth_debug.log` file for detailed logs

## OAuth Flow Debugging Checklist

### 1. Login Initiation (Frontend → Auth Service)
- [ ] User clicks login button
- [ ] Frontend redirects to `/auth/login`
- [ ] Auth service generates OAuth state
- [ ] Redirect to Google OAuth

### 2. OAuth Callback (Google → Auth Service)
- [ ] Google returns with authorization code
- [ ] Auth service exchanges code for tokens
- [ ] User info retrieved from Google
- [ ] JWT token created
- [ ] Redirect back to frontend

### 3. Protected Resource Access (Frontend → Resource Service)
- [ ] Frontend sends JWT token in Authorization header
- [ ] Resource service validates JWT token
- [ ] Role-based access control applied
- [ ] Protected data returned

## Common Debug Points

### Check These Variables:
- `authorization_code` - in OAuth callback
- `access_token` - from Google token exchange  
- `id_token` - Google ID token with user info
- `jwt_token` - Your application's JWT token
- `user_info` - Decoded user information
- `user_role` - Assigned user role

### Network Calls to Monitor:
- `GET /auth/login` - Login initiation
- `GET /auth/callback` - OAuth callback
- `POST /auth/validate` - Token validation
- `GET /api/user-resources` - Protected resources
- `GET /api/admin-resources` - Admin resources

## Tips:
1. Use browser developer tools to inspect network requests
2. Check console logs in browser for frontend errors
3. Monitor the terminal windows for backend logs
4. Use Postman to test API endpoints directly
5. Check the `oauth_debug.log` file for detailed flow traces

## Troubleshooting:
- If debugger doesn't attach, check that debugpy is installed: `pip install debugpy`
- If breakpoints aren't hit, verify the service is running in debug mode
- For CORS issues, check the browser console and backend CORS configuration
