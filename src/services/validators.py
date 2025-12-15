"""
Validators Module - Content Robot v7.1
Provides input validation, security checks, and type enforcement.
"""
import re
from typing import Optional, Dict, Any, Tuple
from functools import wraps
from flask import request, jsonify

# ==============================================================================
# REGEX PATTERNS
# ==============================================================================

class ValidationPatterns:
    """Regex patterns for input validation."""
    
    # API Keys: Generally alphanumeric with hyphens/underscores, 20-100 chars
    API_KEY = re.compile(r'^[A-Za-z0-9_\-]{20,100}$')
    
    # Google Project ID: lowercase, numbers, hyphens
    GOOGLE_PROJECT_ID = re.compile(r'^[a-z0-9\-]{6,30}$')
    
    # URLs: Basic HTTP/HTTPS validation
    URL = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    # WordPress username: alphanumeric, underscore, hyphen, 3-60 chars
    USERNAME = re.compile(r'^[A-Za-z0-9_\-]{3,60}$')
    
    # RSS Feed name: letters, numbers, spaces, basic punctuation
    FEED_NAME = re.compile(r'^[\w\s\-\.]{3,100}$', re.UNICODE)


# ==============================================================================
# SECURITY FLAGS (Global State)
# ==============================================================================

class SecurityFlags:
    """Global security state management."""
    
    _flags: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def set_alert(cls, session_id: str, field: str, reason: str) -> None:
        """Set a security alert flag."""
        if session_id not in cls._flags:
            cls._flags[session_id] = {}
        cls._flags[session_id][field] = {
            'is_security_alert_active': True,
            'reason': reason,
            'field': field
        }
    
    @classmethod
    def clear_alert(cls, session_id: str, field: Optional[str] = None) -> None:
        """Clear security alerts."""
        if session_id in cls._flags:
            if field:
                cls._flags[session_id].pop(field, None)
            else:
                cls._flags.pop(session_id, None)
    
    @classmethod
    def get_alerts(cls, session_id: str) -> Dict[str, Any]:
        """Get all alerts for a session."""
        return cls._flags.get(session_id, {})
    
    @classmethod
    def has_alerts(cls, session_id: str) -> bool:
        """Check if session has any active alerts."""
        return bool(cls._flags.get(session_id))


# ==============================================================================
# VALIDATORS
# ==============================================================================

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_api_key(key: str, provider: str = "generic") -> Tuple[bool, Optional[str]]:
        """
        Validate API key format.
        
        Args:
            key: API key to validate
            provider: Provider name for specific validation
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not key or not isinstance(key, str):
            return False, "API key cannot be empty"
        
        key = key.strip()
        
        if len(key) < 20:
            return False, "API key too short (minimum 20 characters)"
        
        if not ValidationPatterns.API_KEY.match(key):
            return False, "API key contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_url(url: str) -> Tuple[bool, Optional[str]]:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return False, "URL cannot be empty"
        
        url = url.strip()
        
        if not ValidationPatterns.URL.match(url):
            return False, "Invalid URL format"
        
        return True, None
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        if not ValidationPatterns.USERNAME.match(username):
            return False, "Username contains invalid characters or is too short"
        
        return True, None
    
    @staticmethod
    def validate_cycle_interval(minutes: int) -> Tuple[bool, Optional[str]]:
        """
        Validate cycle interval.
        
        Args:
            minutes: Interval in minutes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        MIN_INTERVAL = 30  # 30 minutes
        MAX_INTERVAL = 1440  # 24 hours
        
        if not isinstance(minutes, (int, float)):
            return False, "Interval must be a number"
        
        minutes = int(minutes)
        
        if minutes < MIN_INTERVAL:
            return False, f"Interval too short (minimum {MIN_INTERVAL} minutes)"
        
        if minutes > MAX_INTERVAL:
            return False, f"Interval too long (maximum {MAX_INTERVAL} minutes / 24 hours)"
        
        return True, None
    
    @staticmethod
    def validate_feed_name(name: str) -> Tuple[bool, Optional[str]]:
        """Validate RSS feed name."""
        if not name or not isinstance(name, str):
            return False, "Feed name cannot be empty"
        
        name = name.strip()
        
        if not ValidationPatterns.FEED_NAME.match(name):
            return False, "Feed name contains invalid characters"
        
        return True, None


# ==============================================================================
# DECORATORS
# ==============================================================================

def requires_api_key(provider_key: str):
    """
    Decorator to ensure API key exists and is valid before executing endpoint.
    
    Args:
        provider_key: Settings key for the API (e.g., 'google_api_key')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from src.config.database import get_db
            from src.models.schema import SystemSettings
            
            db = get_db()
            try:
                setting = db.query(SystemSettings).filter(
                    SystemSettings.key == provider_key
                ).first()
                
                api_key = setting.value if setting else None
                
                if not api_key or api_key.strip() == "":
                    return jsonify({
                        'success': False,
                        'error': f'API key not configured: {provider_key}',
                        'blocked': True
                    }), 403
                
                # Validate format
                is_valid, error = InputValidator.validate_api_key(api_key)
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': error,
                        'blocked': True
                    }), 403
                
                return f(*args, **kwargs)
            finally:
                db.close()
        
        return decorated_function
    return decorator


def validate_request_data(schema: Dict[str, type]):
    """
    Decorator to validate request JSON data against a schema.
    
    Args:
        schema: Dictionary mapping field names to expected types
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            for field, expected_type in schema.items():
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
                
                if not isinstance(data[field], expected_type):
                    return jsonify({
                        'success': False,
                        'error': f'Invalid type for {field}: expected {expected_type.__name__}'
                    }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
