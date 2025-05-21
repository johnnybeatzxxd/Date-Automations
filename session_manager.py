import os
import json
import pickle
from datetime import datetime
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SessionManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        self.registry_file = self.sessions_dir / "sessions.json"
        self.load_registry()
        
    def load_registry(self):
        """Load the sessions registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
            self.save_registry()
            
    def save_registry(self):
        """Save the sessions registry"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=4, ensure_ascii=False)
            
    def execute_script_safely(self, driver, script, timeout=5):
        """Execute JavaScript safely with timeout"""
        try:
            return driver.execute_script(script)
        except TimeoutException:
            print("Warning: Script execution timed out")
            return {}
        except Exception as e:
            print(f"Warning: Script execution failed: {e}")
            return {}
            
    def save_session(self, driver, session_name=None):
        """Save browser session data"""
        if not session_name:
            session_name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        session_path = self.sessions_dir / session_name
        if session_path.exists():
            raise ValueError(f"Session {session_name} already exists")
            
        session_path.mkdir(parents=True)
        
        try:
            # Get current URL
            current_url = driver.current_url
            
            # Get all storage data
            storage_data = {
                "cookies": driver.get_cookies(),
                "localStorage": self.execute_script_safely(driver, """
                    let data = {};
                    try {
                        for (let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            data[key] = localStorage.getItem(key);
                        }
                    } catch (e) {
                        console.error('localStorage error:', e);
                    }
                    return data;
                """),
                "sessionStorage": self.execute_script_safely(driver, """
                    let data = {};
                    try {
                        for (let i = 0; i < sessionStorage.length; i++) {
                            const key = sessionStorage.key(i);
                            data[key] = sessionStorage.getItem(key);
                        }
                    } catch (e) {
                        console.error('sessionStorage error:', e);
                    }
                    return data;
                """),
                "indexedDB": self.execute_script_safely(driver, """
                    return new Promise((resolve) => {
                        try {
                            const request = indexedDB.databases();
                            request.onsuccess = () => resolve(request.result);
                            request.onerror = () => resolve([]);
                        } catch (e) {
                            resolve([]);
                        }
                    });
                """)
            }
            
            # Save storage data
            with open(session_path / "storage.json", "w", encoding='utf-8') as f:
                json.dump(storage_data, f, indent=4, ensure_ascii=False)
                
            # Save metadata
            metadata = {
                "created_at": datetime.now().isoformat(),
                "user_agent": driver.execute_script("return navigator.userAgent"),
                "session_name": session_name,
                "url": current_url,
                "platform": os.name
            }
            
            with open(session_path / "metadata.json", "w", encoding='utf-8') as f:
                json.dump(metadata, f, indent=4, ensure_ascii=False)
                
            # Add to registry
            self.registry[session_name] = {
                "created_at": metadata["created_at"],
                "url": current_url,
                "platform": os.name,
                "last_used": None
            }
            self.save_registry()
            
            return session_name
            
        except Exception as e:
            print(f"Warning: Error saving session: {e}")
            if session_path.exists():
                try:
                    import shutil
                    shutil.rmtree(session_path)
                except:
                    pass
            return None
            
    def load_session(self, driver, session_name):
        """Load saved session into browser"""
        session_path = self.sessions_dir / session_name
        
        if not session_path.exists():
            raise FileNotFoundError(f"Session {session_name} not found")
            
        try:
            # Load storage data
            with open(session_path / "storage.json", "r", encoding='utf-8') as f:
                storage_data = json.load(f)
            
            # Load metadata
            with open(session_path / "metadata.json", "r", encoding='utf-8') as f:
                metadata = json.load(f)
            
            # First navigate to the original URL
            if metadata.get('url'):
                driver.get(metadata['url'])
            
            # Add cookies
            for cookie in storage_data.get('cookies', []):
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Warning: Could not add cookie: {e}")
            
            # Restore localStorage
            if storage_data.get('localStorage'):
                self.execute_script_safely(driver, """
                    const data = arguments[0];
                    try {
                        for (const [key, value] of Object.entries(data)) {
                            localStorage.setItem(key, value);
                        }
                    } catch (e) {
                        console.error('localStorage restore error:', e);
                    }
                """, storage_data['localStorage'])
            
            # Restore sessionStorage
            if storage_data.get('sessionStorage'):
                self.execute_script_safely(driver, """
                    const data = arguments[0];
                    try {
                        for (const [key, value] of Object.entries(data)) {
                            sessionStorage.setItem(key, value);
                        }
                    } catch (e) {
                        console.error('sessionStorage restore error:', e);
                    }
                """, storage_data['sessionStorage'])
            
            # Update last used timestamp
            self.registry[session_name]["last_used"] = datetime.now().isoformat()
            self.save_registry()
            
            # Refresh the page to apply all changes
            driver.refresh()
            
        except Exception as e:
            print(f"Warning: Error loading session: {e}")
            
    def list_sessions(self):
        """List all available sessions"""
        return [
            {
                "name": name,
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "url": data["url"],
                "platform": data["platform"]
            }
            for name, data in self.registry.items()
        ]
        
    def delete_session(self, session_name):
        """Delete a session"""
        if session_name not in self.registry:
            raise ValueError(f"Session {session_name} not found")
            
        session_path = self.sessions_dir / session_name
        if session_path.exists():
            import shutil
            shutil.rmtree(session_path)
            
        del self.registry[session_name]
        self.save_registry() 