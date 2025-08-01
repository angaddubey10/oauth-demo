"""
Frontend Service
Serves the UI and handles user interactions
"""
import os
import json
import requests
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS

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

CORS(app)
app.secret_key = os.environ.get("FLASK_SECRET", config['security']['flask_secret'])

# Service URLs from config
AUTH_SERVICE_URL = config['services']['auth_service_url']
RESOURCE_SERVICE_URL = config['services']['resource_service_url']

class APIClient:
    """Client for communicating with backend services"""
    
    @staticmethod
    def call_auth_service(endpoint, method='GET', data=None, token=None):
        """Make API call to auth service"""
        url = f"{AUTH_SERVICE_URL}{endpoint}"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, json=data, headers=headers)
            
            return response.json() if response.status_code < 400 else None
        except Exception as e:
            print(f"Auth service call failed: {e}")
            return None
    
    @staticmethod
    def call_resource_service(endpoint, method='GET', token=None):
        """Make API call to resource service"""
        url = f"{RESOURCE_SERVICE_URL}{endpoint}"
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            
            return response.json() if response.status_code < 400 else None
        except Exception as e:
            print(f"Resource service call failed: {e}")
            return None

@app.route('/')
def index():
    """Home page - redirect based on authentication status"""
    token = session.get('token')
    if token:
        # Verify token with auth service
        result = APIClient.call_auth_service('/auth/verify', 'POST', {'token': token})
        if result and result.get('valid'):
            return redirect(url_for('dashboard'))
    
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Login page"""
    error = request.args.get('error')
    error_message = {
        'state_mismatch': 'Authentication failed due to security check. Please try again.',
        'no_code': 'Authentication was cancelled or failed.',
        'token_exchange_failed': 'Failed to complete authentication with Google.',
        'invalid_token': 'Authentication token is invalid.',
        'internal_error': 'An internal error occurred during authentication.'
    }.get(error, '')
    
    return render_template('login.html', error=error_message)

@app.route('/auth/initiate')
def initiate_auth():
    """Initiate authentication with auth service"""
    result = APIClient.call_auth_service('/auth/login')
    if result and 'auth_url' in result:
        return redirect(result['auth_url'])
    
    return redirect(url_for('login', error='auth_service_error'))

@app.route('/auth/success')
def auth_success():
    """Handle successful authentication callback"""
    token = request.args.get('token')
    if not token:
        return redirect(url_for('login', error='no_token'))
    
    # Verify token
    result = APIClient.call_auth_service('/auth/verify', 'POST', {'token': token})
    if not result or not result.get('valid'):
        return redirect(url_for('login', error='invalid_token'))
    
    # Store token in session
    session['token'] = token
    session['user'] = result['user']
    
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    token = session.get('token')
    user = session.get('user')
    
    if not token or not user:
        return redirect(url_for('login'))
    
    # Verify token is still valid
    result = APIClient.call_auth_service('/auth/verify', 'POST', {'token': token})
    if not result or not result.get('valid'):
        session.clear()
        return redirect(url_for('login', error='session_expired'))
    
    return render_template('dashboard.html', user=user)

@app.route('/api/user/resources')
def get_user_resources():
    """Get user resources from resource service"""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = APIClient.call_resource_service('/resources/user', token=token)

    resp = jsonify(result) if result else (jsonify({'error': 'Service unavailable'}), 503)
    return resp

@app.route('/api/admin/resources')
def get_admin_resources():
    """Get admin resources from resource service"""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = APIClient.call_resource_service('/resources/admin', token=token)
    return jsonify(result) if result else jsonify({'error': 'Service unavailable'}), 503

@app.route('/api/user/profile')
def get_user_profile():
    """Get user profile from resource service"""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = APIClient.call_resource_service('/user/profile', token=token)
    return jsonify(result) if result else (jsonify({'error': 'Service unavailable'}), 503)

@app.route('/api/admin/stats')
def get_admin_stats():
    """Get admin statistics from resource service"""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = APIClient.call_resource_service('/admin/stats', token=token)
    return jsonify(result) if result else jsonify({'error': 'Service unavailable'}), 503

@app.route('/api/admin/users')
def get_admin_users():
    """Get user management data from resource service"""
    token = session.get('token')
    if not token:
        return jsonify({'error': 'Not authenticated'}), 401
    
    result = APIClient.call_resource_service('/admin/users', token=token)
    return jsonify(result) if result else jsonify({'error': 'Service unavailable'}), 503

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'frontend'})

if __name__ == '__main__':
    print("Starting Frontend Service on port 3000")
    app.run(debug=True, port=3000)
