# Google OAuth Setup Guide

## The Problem
You're getting "Authentication failed due to security check" because the Google OAuth configuration in Google Cloud Console doesn't match your application's redirect URI.

## Current Configuration Issues
1. **Redirect URI Mismatch**: Your Google OAuth client is configured with `http://localhost` but your app expects `http://localhost:5001/auth/callback`
2. **Missing Authorized Redirect URIs**: The callback URL needs to be explicitly allowed in Google Cloud Console

## Fix Steps

### 1. Update Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" → "Credentials"
3. Find your OAuth 2.0 Client ID: `318585267769-6mmqth7joogcnacfs02t24ids0m1859q.apps.googleusercontent.com`
4. Click on it to edit
5. In "Authorized redirect URIs", add these URLs:
   - `http://localhost:5001/auth/callback`
   - `http://localhost:3000/auth/success` (optional, for frontend handling)
6. Save the changes

### 2. Configuration Management
The application uses `config.json` for configuration. Your current configuration looks good:


**Important**: Update the `security` section with strong, unique keys for production use.

### 3. Test the Setup
1. Make sure all services are running:
   - Auth Service: http://localhost:5001
   - Resource Service: http://localhost:5002  
   - Frontend: http://localhost:3000
2. Visit http://localhost:3000
3. Click "Sign in with Google"
4. Check the auth service logs for debugging information

### 4. Troubleshooting
If you still get errors, check:
- Network connectivity to Google OAuth servers
- Browser console for JavaScript errors
- Auth service logs (now includes detailed debugging)
- Make sure redirect URIs exactly match (including ports)

### 5. Security Notes
- Never commit OAuth secrets to version control
- Use HTTPS in production
- Consider using more secure session management
- Implement proper CSRF protection for production use

## Next Steps After OAuth Fix
1. Test the complete authentication flow
2. Verify role-based access (admin vs user)
3. Test token refresh functionality
4. Test logout functionality
