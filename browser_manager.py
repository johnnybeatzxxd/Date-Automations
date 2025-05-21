from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

class BrowserManager:
    def __init__(self):
        self.driver = None
        
    def setup_browser(self):
        """Setup and return a new browser instance"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1020,720")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        return self.driver
        
    def close_browser(self):
        """Close the browser instance"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def wait_for_user_login(self):
        """Wait for user to complete login manually"""
        print("\nPlease login to the website manually.")
        print("Press 'X' when you're done logging in...")
        
        while True:
            user_input = input().strip().upper()
            if user_input == 'X':
                # Give a small delay to ensure all cookies are set
                time.sleep(2)
                return True 