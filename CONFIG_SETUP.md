# Configuration Setup Guide

## Overview
This application now uses a `config.json` file to store all secrets and configuration values. This file is excluded from git to keep your credentials secure.

## Setup Steps

### 1. Create Configuration File
Copy the sample configuration file and customize it with your credentials:

```powershell
# Copy the sample configuration
Copy-Item config.sample.json config.json
```

### 2. Update Configuration Values
Edit `config.json` with your actual values:

```json
{
  "google_oauth": {
    "client_id": "your-actual-google-client-id",
    "client_secret": "your-actual-google-client-secret",
    "redirect_uri": "http://localhost:5001/auth/callback",
    "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "scope": "openid email profile"
  },
  "security": {
    "flask_secret": "your-secure-flask-secret-key-here",
    "jwt_secret": "your-secure-jwt-secret-key-here"
  },
  "services": {
    "frontend_url": "http://localhost:3000",
    "auth_service_url": "http://localhost:5001",
    "resource_service_url": "http://localhost:5002"
  },
  "user_roles": {
    "admin@example.com": "admin",
    "your-admin-email@gmail.com": "admin"
  }
}
```

### 3. Required Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Set application type to "Web application"
6. Add authorized redirect URI: `http://localhost:5001/auth/callback`
7. Copy the Client ID and Client Secret to your `config.json`

### 4. Security Recommendations
- **Generate strong secrets**: Use a password generator for flask_secret and jwt_secret
- **Never commit config.json**: The file is already in .gitignore
- **Environment variables**: For production, use environment variables instead of config.json
- **Rotate secrets**: Regularly update your secrets

### 5. Environment Variable Override
You can still override configuration values with environment variables:
- `FLASK_SECRET` - Override flask_secret
- `JWT_SECRET` - Override jwt_secret

### 6. Production Deployment
For production:
1. Don't use config.json in production
2. Use environment variables or a secure secret management service
3. Set `SESSION_COOKIE_SECURE=True` for HTTPS
4. Use a proper database instead of in-memory storage
5. Enable proper logging and monitoring

## File Structure
```
oauth-demo/
├── config.json              # Your actual configuration (excluded from git)
├── config.sample.json       # Sample configuration (safe to commit)
├── .gitignore               # Excludes config.json from git
├── auth-service/
│   └── app.py              # Updated to use config.json
├── frontend/
│   └── app.py              # Updated to use config.json
└── resource-service/
    └── app.py              # Updated to use config.json
```

## Troubleshooting

### Config file not found
If you see "config.json not found" error:
1. Make sure you copied `config.sample.json` to `config.json`
2. Ensure the file is in the root directory of the project

### Invalid JSON error
If you see "Invalid JSON" error:
1. Check your JSON syntax in `config.json`
2. Use an online JSON validator to verify the format
3. Ensure all strings are properly quoted

### OAuth errors
If Google OAuth fails:
1. Verify your client_id and client_secret are correct
2. Check that redirect_uri matches exactly in Google Cloud Console
3. Ensure the Google+ API is enabled in your project

## Security Benefits
✅ Secrets are no longer in source code  
✅ config.json is excluded from git  
✅ Easy to manage different environments  
✅ Environment variables can still override values  
✅ Sample file shows required structure without exposing secrets
