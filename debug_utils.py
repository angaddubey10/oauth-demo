"""
Debug utilities for OAuth Demo
Provides logging and debugging helpers
"""
import logging
import functools
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oauth_debug.log'),
        logging.StreamHandler()
    ]
)

def debug_oauth_flow(func):
    """Decorator to log OAuth flow steps"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"🔍 OAUTH FLOW: Entering {func.__name__}")
        logger.debug(f"   Args: {args}")
        logger.debug(f"   Kwargs: {kwargs}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"✅ OAUTH FLOW: {func.__name__} completed in {execution_time:.3f}s")
            logger.debug(f"   Result: {result}")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ OAUTH FLOW: {func.__name__} failed after {execution_time:.3f}s")
            logger.error(f"   Error: {str(e)}")
            raise
    return wrapper

def log_request_details(request):
    """Log incoming request details"""
    logger = logging.getLogger('request_details')
    logger.info(f"📥 REQUEST: {request.method} {request.url}")
    logger.debug(f"   Headers: {dict(request.headers)}")
    logger.debug(f"   Args: {dict(request.args)}")
    if request.is_json:
        logger.debug(f"   JSON: {request.get_json()}")

def log_response_details(response, status_code=None):
    """Log outgoing response details"""
    logger = logging.getLogger('response_details')
    if status_code:
        logger.info(f"📤 RESPONSE: Status {status_code}")
    logger.debug(f"   Response: {response}")

def debug_token_flow(token_data):
    """Debug JWT token creation/validation"""
    logger = logging.getLogger('token_debug')
    logger.info("🎫 TOKEN DEBUG:")
    logger.debug(f"   Token Data: {token_data}")
    logger.debug(f"   Timestamp: {datetime.now().isoformat()}")
