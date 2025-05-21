from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from session_manager import SessionManager
import tempfile
import os
import shutil
import time
import platform

def get_session_count() -> int:
    """
    Get the number of available sessions.
    
    Returns:
        int: Number of available sessions
    """
    try:
        session_manager = SessionManager()
        return len(session_manager.list_sessions())
    except Exception as e:
        print(f"Error getting session count: {e}")
        return 0

def load_session_by_index(index: int) -> webdriver.Chrome:
    """
    Load a session by its index and return a configured WebDriver instance.
    
    Args:
        index (int): The index of the session to load (0-based)
        
    Returns:
        webdriver.Chrome: Configured WebDriver instance with the session loaded
        None: If the index is out of range or session doesn't exist
    """
    try:
        # Initialize session manager
        session_manager = SessionManager()
        
        # Get list of available sessions
        sessions = session_manager.list_sessions()
        
        # Check if index is valid
        if index < 0 or index >= len(sessions):
            print(f"Error: Session index {index} is out of range. Available sessions: {len(sessions)}")
            return None
            
        # Get the selected session
        selected_session = sessions[index]
        
        # Create a unique temporary directory for this session
        temp_dir = tempfile.mkdtemp(prefix=f"chrome_session_{selected_session['name']}_")
        
        # Setup browser with anti-detection options
        chrome_options = Options()
        
        # Common options for all platforms
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-save-password-bubble")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-features=IsolateOrigins,site-per-process")
        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
        
        # Platform-specific options
        if platform.system().lower() == 'linux':
            chrome_options.add_argument("--headless=new")  # Required for some Linux environments
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--no-zygote")
            chrome_options.add_argument("--single-process")
            # Set display for X11
            os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':0')
        
        # Add experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("detach", True)
        
        # Create driver instance
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Load the session
        session_manager.load_session(driver, selected_session['name'])
        
        print(f"Loaded session: {selected_session['name']}")
        print(f"URL: {selected_session['url']}")
        
        # Store the temporary directory path in the driver for cleanup
        driver._temp_dir = temp_dir
        
        return driver
        
    except Exception as e:
        print(f"Error loading session: {e}")
        # Clean up temporary directory if it exists
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except PermissionError:
                print("Note: Some temporary files could not be cleaned up immediately. They will be removed automatically by the system.")
        return None

def cleanup_session(driver):
    """Clean up the session's temporary directory"""
    if hasattr(driver, '_temp_dir') and os.path.exists(driver._temp_dir):
        try:
            # First try to close all Chrome processes gracefully
            driver.quit()
            
            # Give Chrome a moment to release file handles
            time.sleep(2)  # Increased sleep time
            
            # Try to remove the directory
            try:
                shutil.rmtree(driver._temp_dir)
            except PermissionError:
                print("Note: Some temporary files could not be cleaned up immediately. They will be removed automatically by the system.")
                
        except Exception as e:
            print(f"Note: Some temporary files could not be cleaned up immediately. They will be removed automatically by the system.")

# Example usage:
if __name__ == "__main__":
    # Get number of available sessions
    session_count = get_session_count()
    print(f"Available sessions: {session_count}")
    
    # Load first session
    driver1 = load_session_by_index(0)
    if driver1:
        try:
            # Your automation code for first session
            pass
        finally:
            cleanup_session(driver1)

    # Load second session
    driver2 = load_session_by_index(1)
    if driver2:
        try:
            # Your automation code for second session
            pass
        finally:
            cleanup_session(driver2)