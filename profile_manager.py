import os
import json
import shutil
import platform
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ProfileManager:
    def __init__(self):
        # Use relative path for profiles directory
        self.base_dir = Path(__file__).parent
        self.profiles_dir = self.base_dir / "chrome_profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        self.registry_file = self.profiles_dir / "profiles.json"
        self.load_registry()
        
    def load_registry(self):
        """Load the profiles registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
            self.save_registry()
            
    def save_registry(self):
        """Save the profiles registry"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)
            
    def create_profile(self, profile_name=None):
        """Create a new Chrome profile"""
        if not profile_name:
            profile_name = f"profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        profile_path = self.profiles_dir / profile_name
        if profile_path.exists():
            raise ValueError(f"Profile {profile_name} already exists")
            
        # Create profile directory
        profile_path.mkdir(parents=True)
        
        # Add to registry
        self.registry[profile_name] = {
            "created_at": datetime.now().isoformat(),
            "path": str(profile_path.relative_to(self.base_dir)),
            "last_used": None,
            "platform": platform.system()
        }
        self.save_registry()
        
        return profile_name
        
    def get_profile_path(self, profile_name):
        """Get the path for a profile"""
        if profile_name not in self.registry:
            raise ValueError(f"Profile {profile_name} not found")
        return self.profiles_dir / profile_name
        
    def list_profiles(self):
        """List all available profiles"""
        return [
            {
                "name": name,
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "platform": data.get("platform", "Unknown")
            }
            for name, data in self.registry.items()
        ]
        
    def delete_profile(self, profile_name):
        """Delete a profile"""
        if profile_name not in self.registry:
            raise ValueError(f"Profile {profile_name} not found")
            
        profile_path = self.get_profile_path(profile_name)
        if profile_path.exists():
            shutil.rmtree(profile_path)
            
        del self.registry[profile_name]
        self.save_registry()
        
    def setup_browser(self, profile_name):
        """Setup a browser instance with the specified profile"""
        profile_path = self.get_profile_path(profile_name)
        
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1020,720")
        
        # Additional options to prevent crashes
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-default-apps")
        
        # Platform-specific options
        if platform.system() == "Linux":
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
        
        # Set up Chrome profile with relative paths
        chrome_options.add_argument(f"--user-data-dir={str(self.profiles_dir)}")
        chrome_options.add_argument(f"--profile-directory={profile_name}")
        
        # Add experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Update last used timestamp
        self.registry[profile_name]["last_used"] = datetime.now().isoformat()
        self.save_registry()
        
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            return driver
        except Exception as e:
            # If there's an error, try to clean up the profile directory
            if profile_path.exists():
                try:
                    shutil.rmtree(profile_path)
                except:
                    pass
            raise e 