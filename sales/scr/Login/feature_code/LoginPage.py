import yaml
import os
from pathlib import Path
from sales.utility.WebDriverHelper import WebDriverHelper

def _get_env():
    """Get environment from env var or default to prod"""
    return os.getenv("DVR_ENV", "prod")

class LoginPage(WebDriverHelper):
    def __init__(self, page, cred_key=None, env=None):
        super().__init__(page)
        self.config = self._load_config()
        self.env = env or _get_env()
        self.cred_key = cred_key
        # Only parse credentials if cred_key is provided
        if cred_key:
            self._parse_credentials(cred_key)
        self.test_env_url_sub_str = self.config.get(self.env, {}).get("test_env_url_sub_str")
        
        # Check for command-line override first, then fall back to config
        self.test_env_main_url_sub_str = os.getenv("TEST_ENV_DOMAIN") or self.config.get(self.env, {}).get("test_env_main_url_sub_str")
        
        if not self.test_env_url_sub_str or not self.test_env_main_url_sub_str:
            raise ValueError(f"Environment '{self.env}' not found in config.yaml or URL components are missing")
    
   
    def _load_config(self):
        """Load configuration from config.yaml"""
        # Find project root by looking for config.yaml
        current_path = Path(__file__).resolve()
        while current_path.parent != current_path:
            config_path = current_path.parent / "config.yaml"
            if config_path.exists():
                break
            current_path = current_path.parent
        else:
            # Fallback: go up 5 levels from login.py to project root
            config_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"config.yaml not found. Searched from {Path(__file__).resolve()}")
        
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    
    def _parse_credentials(self, cred_key):
        """Parse and store all credential parts from credential string"""
        cred_string = self.config.get(self.env, {}).get(cred_key, "")
        if not cred_string:
            raise ValueError(f"Credential key '{cred_key}' not found in config for environment '{self.env}'")
        
        parts = cred_string.split("___")
        if len(parts) < 2:
            raise ValueError(f"Invalid credential format for '{cred_key}'. Expected at least 'email___password'")
        
        # Parse required fields
        self.email = parts[0]
        self.password = parts[1]
        
        # Parse optional fields (if available)
        self.user_name = parts[2] if len(parts) > 2 else None
        self.workspace_id = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else None
        self.user_id = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None
        
        # Store any additional parts for future use
        self.additional_data = parts[5:] if len(parts) > 5 else []

    def navigate(self):
        url = "https://"+self.test_env_url_sub_str + self.test_env_main_url_sub_str
        self.page.goto(url)

    def collapseNavBar(self):
        if self.is_element_found("div#collapsed_sidebar[style*='display: none;']"):
            self.page.locator("img[alt='expand_icon']").click()
        self.wait_for_element_to_disappear("div#collapsed_sidebar[style*='display: none;']", self.default_wait_time)

    def login(self):
        # Ensure credentials are parsed before login
        if not self.cred_key:
            raise ValueError("cred_key must be provided to use login() method")
        if not hasattr(self, 'email') or not hasattr(self, 'password'):
            self._parse_credentials(self.cred_key)
        
        self.page.get_by_placeholder("Enter your work email").fill(self.email)
        self.page.locator("#submit-btn").filter(has_text="Continue").click()
        self.page.locator("#auth_user_password").fill(self.password)
        self.page.locator("#submit-btn").filter(has_text="Sign In").click()
        self.page.locator("[alt='superagi_logo']").wait_for()