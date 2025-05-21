import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from session_manager import SessionManager

class CLI:
    def __init__(self):
        self.session_manager = SessionManager()
        self.driver = None
        
    def setup_browser(self):
        """Setup a new browser instance"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1020,720")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Add experimental options
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def display_menu(self):
        """Display the main menu"""
        print("\n=== Browser Session Manager ===")
        print("1. Create new session")
        print("2. Use existing session")
        print("3. Delete session")
        print("4. List sessions")
        print("5. Exit")
        print("=============================")
        
    def create_session(self):
        """Handle session creation"""
        print("\nCreating new session...")
        session_name = input("Enter a name for this session (or press Enter for auto-generated name): ").strip()
        
        try:
            self.driver = self.setup_browser()
            self.driver.get("https://www.google.com")
            
            print("\nBrowser opened.")
            print("\nYou can now:")
            print("1. Navigate to multiple websites")
            print("2. Log in to each website")
            print("3. Set up any desired state (like filling forms, selecting preferences, etc.)")
            print("\nAll website sessions will be saved together when you're done.")
            print("Press Enter when you're finished with all websites...")
            input()
            
            saved_name = self.session_manager.save_session(self.driver, session_name)
            if saved_name:
                print(f"\nSession saved successfully as: {saved_name}")
                print("This session contains all website states you've set up.")
            else:
                print("\nFailed to save session. Please try again.")
                
        except Exception as e:
            print(f"\nError creating session: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
    def use_session(self):
        """Handle using existing session"""
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            print("\nNo sessions found!")
            return
            
        print("\nAvailable sessions:")
        for idx, session in enumerate(sessions, 1):
            last_used = session['last_used'] or 'Never'
            print(f"{idx}. {session['name']} (Created: {session['created_at']}, Last used: {last_used})")
            print(f"   URL: {session['url']}")
            
        while True:
            try:
                choice = int(input("\nSelect a session number: "))
                if 1 <= choice <= len(sessions):
                    selected_session = sessions[choice - 1]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
                
        try:
            self.driver = self.setup_browser()
            self.session_manager.load_session(self.driver, selected_session['name'])
            
            print(f"\nLoaded session: {selected_session['name']}")
            print("Press Enter to close the browser...")
            input()
            
        except Exception as e:
            print(f"\nError using session: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
    def delete_session(self):
        """Handle session deletion"""
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            print("\nNo sessions found!")
            return
            
        print("\nAvailable sessions:")
        for idx, session in enumerate(sessions, 1):
            print(f"{idx}. {session['name']} (Created: {session['created_at']})")
            
        while True:
            try:
                choice = int(input("\nSelect a session number to delete: "))
                if 1 <= choice <= len(sessions):
                    selected_session = sessions[choice - 1]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
                
        confirm = input(f"\nAre you sure you want to delete session '{selected_session['name']}'? (y/N): ").strip().lower()
        if confirm == 'y':
            try:
                self.session_manager.delete_session(selected_session['name'])
                print(f"\nSession '{selected_session['name']}' deleted successfully.")
            except Exception as e:
                print(f"\nError deleting session: {e}")
        else:
            print("\nDeletion cancelled.")
        
    def run(self):
        """Run the CLI application"""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                self.create_session()
            elif choice == "2":
                self.use_session()
            elif choice == "3":
                self.delete_session()
            elif choice == "4":
                sessions = self.session_manager.list_sessions()
                if sessions:
                    print("\nAvailable sessions:")
                    for session in sessions:
                        last_used = session['last_used'] or 'Never'
                        print(f"- {session['name']} (Created: {session['created_at']}, Last used: {last_used})")
                        print(f"  URL: {session['url']}")
                else:
                    print("\nNo sessions found!")
            elif choice == "5":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.") 