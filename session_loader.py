from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from session_manager import SessionManager

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
        
        # Setup browser with anti-detection options
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1020,720")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Add experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        # Create driver instance
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Load the session
        session_manager.load_session(driver, selected_session['name'])
        
        print(f"Loaded session: {selected_session['name']}")
        print(f"URL: {selected_session['url']}")
        
        return driver
        
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # Load the first session (index 0)
    driver = load_session_by_index(1)
    
    if driver:
        try:
            # Your automation code here
            print("Session loaded successfully!")
            input("Press Enter to close the browser...")
        finally:
            driver.quit()
    else:
        print("Failed to load session") 