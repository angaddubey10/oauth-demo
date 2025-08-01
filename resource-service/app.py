"""
Resource Service
Handles protected resources with role-based access control
"""
import os
import jwt
import json
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
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

CORS(app)  # Enable CORS for frontend communication

# Configuration
JWT_SECRET = os.environ.get("JWT_SECRET", config['security']['jwt_secret'])

# Sample data stores (in production, use a proper database)
RESOURCES = {
    'user_documents': [
        {
            'id': 1,
            'title': 'Personal Document 1',
            'content': 'This is a user-accessible document.',
            'type': 'document',
            'created_at': '2025-01-01T10:00:00Z'
        },
        {
            'id': 2,
            'title': 'User Report',
            'content': 'Monthly user activity report.',
            'type': 'report',
            'created_at': '2025-01-15T14:30:00Z'
        },
        {
            'id': 3,
            'title': 'Project Files',
            'content': 'Access to your project files and documents.',
            'type': 'files',
            'created_at': '2025-01-20T09:15:00Z'
        }
    ],
    'admin_resources': [
        {
            'id': 101,
            'title': 'System Configuration',
            'content': 'Critical system settings and configurations.',
            'type': 'config',
            'created_at': '2025-01-01T09:00:00Z',
            'sensitive': True
        },
        {
            'id': 102,
            'title': 'User Management Dashboard',
            'content': 'Comprehensive user analytics and management tools.',
            'type': 'dashboard',
            'created_at': '2025-01-10T11:00:00Z',
            'sensitive': True
        },
        {
            'id': 103,
            'title': 'System Logs',
            'content': 'Access to system logs and audit trails.',
            'type': 'logs',
            'created_at': '2025-01-25T16:45:00Z',
            'sensitive': True
        }
    ]
}

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, 'user') or request.user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

def format_api_response(data, message="Success", status="success"):
    """Format consistent API responses"""
    return {
        'status': status,
        'message': message,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'resource-service'})

@app.route('/resources/user', methods=['GET'])
@login_required
def get_user_resources():
    """Get resources available to regular users"""
    resources = RESOURCES['user_documents']
    
    # Add user-specific metadata
    enriched_resources = []
    for resource in resources:
        enriched_resource = resource.copy()
        enriched_resource['access_level'] = 'user'
        enriched_resource['accessible_by'] = request.user['email']
        enriched_resources.append(enriched_resource)
    
    return jsonify(format_api_response(
        enriched_resources, 
        f"Retrieved {len(enriched_resources)} user resources"
    ))

@app.route('/resources/admin', methods=['GET'])
@login_required
@admin_required
def get_admin_resources():
    """Get resources available to admin users"""
    resources = RESOURCES['admin_resources']
    
    # Add admin-specific metadata
    enriched_resources = []
    for resource in resources:
        enriched_resource = resource.copy()
        enriched_resource['access_level'] = 'admin'
        enriched_resource['accessible_by'] = request.user['email']
        enriched_resources.append(enriched_resource)
    
    return jsonify(format_api_response(
        enriched_resources, 
        f"Retrieved {len(enriched_resources)} admin resources"
    ))

@app.route('/resources/all', methods=['GET'])
@login_required
def get_all_accessible_resources():
    """Get all resources accessible to the current user based on their role"""
    user_role = request.user.get('role', 'user')
    
    accessible_resources = RESOURCES['user_documents'].copy()
    
    if user_role == 'admin':
        accessible_resources.extend(RESOURCES['admin_resources'])
    
    # Add metadata
    enriched_resources = []
    for resource in accessible_resources:
        enriched_resource = resource.copy()
        enriched_resource['access_level'] = 'admin' if resource.get('sensitive') else 'user'
        enriched_resource['accessible_by'] = request.user['email']
        enriched_resources.append(enriched_resource)
    
    return jsonify(format_api_response(
        enriched_resources, 
        f"Retrieved {len(enriched_resources)} accessible resources"
    ))

@app.route('/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get current user's profile and stats"""
    user_role = request.user.get('role', 'user')
    
    # Calculate user stats
    total_user_resources = len(RESOURCES['user_documents'])
    total_admin_resources = len(RESOURCES['admin_resources']) if user_role == 'admin' else 0
    
    stats = {
        'total_accessible_resources': total_user_resources + total_admin_resources,
        'user_resources': total_user_resources,
        'admin_resources': total_admin_resources,
        'role': user_role,
        'last_accessed': datetime.utcnow().isoformat() + 'Z'
    }
    
    profile_data = {
        'user_info': {
            'sub': request.user['sub'],
            'email': request.user['email'],
            'name': request.user['name'],
            'picture': request.user.get('picture', ''),
            'role': user_role
        },
        'stats': stats,
        'permissions': {
            'can_access_user_resources': True,
            'can_access_admin_resources': user_role == 'admin',
            'can_manage_users': user_role == 'admin'
        }
    }
    
    return jsonify(format_api_response(profile_data, "Profile retrieved successfully"))

@app.route('/admin/stats', methods=['GET'])
@login_required
@admin_required
def get_system_stats():
    """Get system statistics (admin only)"""
    stats = {
        'total_resources': len(RESOURCES['user_documents']) + len(RESOURCES['admin_resources']),
        'user_resources_count': len(RESOURCES['user_documents']),
        'admin_resources_count': len(RESOURCES['admin_resources']),
        'system_uptime': '5 days, 12 hours',  # Mock data
        'active_users': 15,  # Mock data
        'total_api_calls': 1247,  # Mock data
        'last_updated': datetime.utcnow().isoformat() + 'Z'
    }
    
    return jsonify(format_api_response(stats, "System statistics retrieved"))

@app.route('/admin/users', methods=['GET'])
@login_required
@admin_required
def get_user_management():
    """Get user management data (admin only)"""
    # Mock user data
    users = [
        {
            'id': 1,
            'email': 'user1@example.com',
            'name': 'Regular User',
            'role': 'user',
            'last_login': '2025-01-30T10:30:00Z',
            'status': 'active'
        },
        {
            'id': 2,
            'email': 'admin@example.com',
            'name': 'Admin User',
            'role': 'admin',
            'last_login': '2025-01-31T08:15:00Z',
            'status': 'active'
        },
        {
            'id': 3,
            'email': 'user2@example.com',
            'name': 'Another User',
            'role': 'user',
            'last_login': '2025-01-29T14:45:00Z',
            'status': 'active'
        }
    ]
    
    return jsonify(format_api_response(users, "User list retrieved successfully"))

if __name__ == '__main__':
    print("Starting Resource Service on port 5002")
    app.run(debug=True, port=5002)
