"""
Authentication Service
Handles Google OAuth authentication and JWT token management
"""
import os
import jwt
import json
import requests
import time
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, redirect, session
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_cors import CORS

# Simple in-memory state store for OAuth state management
# In production, use Redis or a proper database
oauth_states = {}

app = Flask(__name__)

# Load configuration from config.json
def load_config():
    """Load configuration from config.json file"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: config.json not found. Copy config.sample.json to config.json and update with your credentials.")
        exit(1)
    except json.JSONDecodeError:
        print("❌ Error: Invalid JSON in config.json")
        exit(1)

config = load_config()

CORS(app, supports_credentials=True, origins=[config['services']['frontend_url']])  # Enable CORS with credentials

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET", config['security']['flask_secret'])
JWT_SECRET = os.environ.get("JWT_SECRET", config['security']['jwt_secret'])

# Session configuration for better security
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# Google OAuth config from config.json
CLIENT_ID = config['google_oauth']['client_id']
CLIENT_SECRET = config['google_oauth']['client_secret']
REDIRECT_URI = config['google_oauth']['redirect_uri']
AUTH_URI = config['google_oauth']['auth_uri']
TOKEN_URI = config['google_oauth']['token_uri']
SCOPE = config['google_oauth']['scope']

# Note: Make sure your Google Cloud Console OAuth 2.0 Client has this redirect URI:
# http://localhost:5001/auth/callback

# Frontend URL for redirects
FRONTEND_URL = config['services']['frontend_url']

# User roles configuration from config.json
USER_ROLES = config['user_roles']

def cleanup_expired_states():
    """Clean up expired OAuth states"""
    current_time = time.time()
    expired_states = [state for state, data in oauth_states.items() 
                     if current_time - data['timestamp'] > 600]  # 10 minutes expiry
    for state in expired_states:
        del oauth_states[state]

def store_oauth_state(state):
    """Store OAuth state with timestamp"""
    cleanup_expired_states()
    oauth_states[state] = {
        'timestamp': time.time(),
        'used': False
    }

def verify_oauth_state(state):
    """Verify and consume OAuth state"""
    cleanup_expired_states()
    if state in oauth_states and not oauth_states[state]['used']:
        oauth_states[state]['used'] = True
        return True
    return False

def get_user_role(email):
    """Determine user role based on email"""
    return USER_ROLES.get(email, 'user')

def create_jwt_token(user_info):
    """Create JWT token for authenticated user"""
    payload = {
        'sub': user_info['sub'],
        'email': user_info['email'],
        'name': user_info['name'],
        'role': user_info['role'],
        'picture': user_info.get('picture', ''),
        'exp': datetime.utcnow() + timedelta(hours=8)  # 8 hour expiry
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth-service'})

@app.route('/auth/config', methods=['GET'])
def get_auth_config():
    """Get OAuth configuration for debugging"""
    return jsonify({
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'auth_uri': AUTH_URI,
        'token_uri': TOKEN_URI,
        'scope': SCOPE,
        'frontend_url': FRONTEND_URL
    })

@app.route('/auth/debug', methods=['GET'])
def debug_oauth():
    """Debug OAuth state for troubleshooting"""
    cleanup_expired_states()
    return jsonify({
        'stored_states_count': len(oauth_states),
        'stored_states': list(oauth_states.keys()),
        'session_has_state': 'oauth_state' in session,
        'session_state': session.get('oauth_state', 'None')
    })

@app.route('/auth/clear', methods=['POST'])
def clear_oauth_state():
    """Clear all OAuth states for troubleshooting"""
    global oauth_states
    oauth_states.clear()
    session.clear()
    return jsonify({'message': 'OAuth states cleared', 'success': True})

@app.route('/auth/login', methods=['GET'])
def initiate_login():
    """Initiate Google OAuth login"""
    state = os.urandom(32).hex()  # Longer state for better security
    store_oauth_state(state)
    
    # Also store in session as backup
    session['oauth_state'] = state
    
    auth_url = (
        f"{AUTH_URI}?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE}"
        f"&state={state}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    
    print(f"Generated OAuth state: {state}")
    print(f"Auth URL: {auth_url}")
    
    return jsonify({'auth_url': auth_url})

@app.route('/auth/callback', methods=['GET'])
def oauth_callback():
    """Handle OAuth callback from Google"""
    try:
        # Debug logging
        print(f"Callback received with args: {request.args}")
        
        # Get state parameter
        state = request.args.get('state')
        session_state = session.get('oauth_state')
        
        print(f"State from request: {state}")
        print(f"State from session: {session_state}")
        print(f"Stored states count: {len(oauth_states)}")
        
        # Verify state using both methods
        state_valid = False
        if state:
            # Primary method: check against stored states
            if verify_oauth_state(state):
                state_valid = True
                print("State verified using stored states")
            # Backup method: check against session
            elif state == session_state:
                state_valid = True
                print("State verified using session backup")
        
        if not state_valid:
            print("State mismatch detected!")
            print(f"Available states: {list(oauth_states.keys())}")
            return redirect(f"{FRONTEND_URL}/login?error=state_mismatch")

        code = request.args.get('code')
        if not code:
            print("No authorization code received")
            return redirect(f"{FRONTEND_URL}/login?error=no_code")
        
        print(f"Authorization code received: {code[:20]}...")

        # Exchange code for tokens
        data = {
            'code': code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code',
        }
        
        print(f"Exchanging code for tokens with redirect_uri: {REDIRECT_URI}")
        token_response = requests.post(TOKEN_URI, data=data)
        print(f"Token response status: {token_response.status_code}")
        
        if token_response.status_code != 200:
            print(f"Token exchange failed: {token_response.text}")
            return redirect(f"{FRONTEND_URL}/login?error=token_exchange_failed")
        
        tokens = token_response.json()
        print("Tokens received successfully")

        # Verify ID token
        try:
            idinfo = id_token.verify_oauth2_token(
                tokens['id_token'], google_requests.Request(), CLIENT_ID,
                clock_skew_in_seconds=60
            )
            print(f"ID token verified for user: {idinfo.get('email')}")
        except ValueError as e:
            print(f"ID token verification failed: {e}")
            return redirect(f"{FRONTEND_URL}/login?error=invalid_token")

        # Create user info with role
        user_email = idinfo.get('email')
        user_role = get_user_role(user_email)
        
        user_info = {
            'sub': idinfo['sub'],
            'email': user_email,
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'role': user_role
        }

        # Create JWT token
        jwt_token = create_jwt_token(user_info)
        print(f"JWT token created for user: {user_email}")
        
        # Clear session state
        session.pop('oauth_state', None)
        
        # Redirect to frontend with token
        return redirect(f"{FRONTEND_URL}/auth/success?token={jwt_token}")
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(f"{FRONTEND_URL}/login?error=internal_error")

@app.route('/auth/verify', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'sub': payload['sub'],
                'email': payload['email'],
                'name': payload['name'],
                'role': payload['role'],
                'picture': payload.get('picture', '')
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Token verification failed'}), 500

@app.route('/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Create new token with extended expiry
        new_token = create_jwt_token({
            'sub': payload['sub'],
            'email': payload['email'],
            'name': payload['name'],
            'role': payload['role'],
            'picture': payload.get('picture', '')
        })
        
        return jsonify({'token': new_token})
        
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 500

if __name__ == '__main__':
    print("Starting Auth Service on port 5001")
    app.run(debug=True, port=5001)
