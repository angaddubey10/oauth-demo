"""
OAuth Diagnosis Script
Run this to test your OAuth setup
"""
import requests
import json

def test_oauth_setup():
    print("🔍 OAuth Demo Diagnosis")
    print("=" * 50)
    
    # Test service health
    services = {
        'Frontend': 'http://localhost:3000/health',
        'Auth Service': 'http://localhost:5001/health', 
        'Resource Service': 'http://localhost:5002/health'
    }
    
    print("\n📊 Service Health Check:")
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Online")
            else:
                print(f"❌ {name}: Offline (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {name}: Offline (Error: {str(e)})")
    
    # Test OAuth configuration
    print("\n🔧 OAuth Configuration:")
    try:
        config_response = requests.get('http://localhost:5001/auth/config', timeout=5)
        if config_response.status_code == 200:
            config = config_response.json()
            print(f"✅ Client ID: {config['client_id']}")
            print(f"✅ Redirect URI: {config['redirect_uri']}")
            print(f"✅ Auth URI: {config['auth_uri']}")
            print(f"✅ Frontend URL: {config['frontend_url']}")
        else:
            print("❌ Could not retrieve OAuth configuration")
    except Exception as e:
        print(f"❌ OAuth config error: {str(e)}")
    
    # Test auth initiation
    print("\n🚀 Auth Flow Test:")
    try:
        auth_response = requests.get('http://localhost:5001/auth/login', timeout=5)
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            if 'auth_url' in auth_data:
                print("✅ Auth URL generation: Working")
                print(f"🔗 Auth URL: {auth_data['auth_url'][:100]}...")
            else:
                print("❌ Auth URL generation: Failed")
        else:
            print("❌ Auth initiation failed")
    except Exception as e:
        print(f"❌ Auth flow error: {str(e)}")
    
    print("\n📋 Next Steps:")
    print("1. Ensure Google Cloud Console has redirect URI: http://localhost:5001/auth/callback")
    print("2. Visit http://localhost:3000 to test the full flow")
    print("3. Check browser console and auth service logs for detailed errors")
    print("\n💡 If you see 'state_mismatch', try clearing browser cookies and try again")

if __name__ == "__main__":
    test_oauth_setup()
