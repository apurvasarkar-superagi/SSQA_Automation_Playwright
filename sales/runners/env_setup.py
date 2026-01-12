"""
Environment setup utilities.
Similar to EnvSetup.java in the Java framework.
"""
import os
import threading
from typing import Optional

class EnvSetup:
    """Thread-local storage for test environment variables and state"""
    
    # Thread-local storage for driver/page
    _page = threading.local()
    
    # Thread-local storage for environment variables
    _jenkins_job_identifier = threading.local()
    _current_user_email = threading.local()
    _current_user_username = threading.local()
    _current_user_workspace_id = threading.local()
    _current_user_password = threading.local()
    
    @staticmethod
    def set_page(page):
        """Set the current page instance for this thread"""
        EnvSetup._page.value = page
    
    @staticmethod
    def get_page():
        """Get the current page instance for this thread"""
        return getattr(EnvSetup._page, 'value', None)
    
    @staticmethod
    def set_jenkins_job_identifier(identifier: str):
        """Set Jenkins job identifier"""
        EnvSetup._jenkins_job_identifier.value = identifier
    
    @staticmethod
    def get_jenkins_job_identifier() -> Optional[str]:
        """Get Jenkins job identifier"""
        return getattr(EnvSetup._jenkins_job_identifier, 'value', None)
    
    @staticmethod
    def set_current_user_email(email: str):
        """Set current user email"""
        EnvSetup._current_user_email.value = email
    
    @staticmethod
    def get_current_user_email() -> Optional[str]:
        """Get current user email"""
        return getattr(EnvSetup._current_user_email, 'value', None)
    
    @staticmethod
    def set_current_user_username(username: str):
        """Set current user username"""
        EnvSetup._current_user_username.value = username
    
    @staticmethod
    def get_current_user_username() -> Optional[str]:
        """Get current user username"""
        return getattr(EnvSetup._current_user_username, 'value', None)
    
    @staticmethod
    def set_current_user_workspace_id(workspace_id: str):
        """Set current user workspace ID"""
        EnvSetup._current_user_workspace_id.value = workspace_id
    
    @staticmethod
    def get_current_user_workspace_id() -> Optional[str]:
        """Get current user workspace ID"""
        return getattr(EnvSetup._current_user_workspace_id, 'value', None)
    
    @staticmethod
    def set_current_user_password(password: str):
        """Set current user password"""
        EnvSetup._current_user_password.value = password
    
    @staticmethod
    def get_current_user_password() -> Optional[str]:
        """Get current user password"""
        return getattr(EnvSetup._current_user_password, 'value', None)
    
    @staticmethod
    def get_env() -> str:
        """Get current environment (prod or staging)"""
        return os.getenv("DVR_ENV", "prod")
    
    @staticmethod
    def get_test_env_domain() -> Optional[str]:
        """Get test environment domain override"""
        return os.getenv("TEST_ENV_DOMAIN")
