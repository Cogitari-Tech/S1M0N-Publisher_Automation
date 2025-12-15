
import pytest
from unittest.mock import patch
from src.services.deployment_service import DeploymentService

def test_prepare_build_success():
    with patch('src.services.deployment_service.settings') as mock_settings:
        mock_settings.GOOGLE_API_KEY = "valid_key"
        mock_settings.FLASK_SECRET_KEY = "valid_secret"
        mock_settings.WORDPRESS_URL = "http://localhost/wp"
        
        assert DeploymentService.prepare_build('PROD') is True

def test_prepare_build_fail_prod():
    with patch('src.services.deployment_service.settings') as mock_settings:
        mock_settings.GOOGLE_API_KEY = None # Simulating missing key
        mock_settings.FLASK_SECRET_KEY = "valid"
        
        with pytest.raises(EnvironmentError, match="Missing keys"):
            DeploymentService.prepare_build('PROD')

def test_prepare_build_warn_dev():
    with patch('src.services.deployment_service.settings') as mock_settings:
        mock_settings.GOOGLE_API_KEY = None
        mock_settings.FLASK_SECRET_KEY = "valid"
        
        # In DEV, it logs warning and returns False, but does NOT raise
        assert DeploymentService.prepare_build('DEV') is False
