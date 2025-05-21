import sys
import time
from profile_manager import ProfileManager

class CLI:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.driver = None
        
    def display_menu(self):
        """Display the main menu"""
        print("\n=== Chrome Profile Manager ===")
        print("1. Create new profile")
        print("2. Use existing profile")
        print("3. Delete profile")
        print("4. List profiles")
        print("5. Exit")
        print("=============================")
        
    def create_profile(self):
        """Handle profile creation"""
        print("\nCreating new profile...")
        profile_name = input("Enter a name for this profile (or press Enter for auto-generated name): ").strip()
        
        try:
            profile_name = self.profile_manager.create_profile(profile_name)
            print(f"\nProfile created: {profile_name}")
            
            # Open browser with new profile
            self.driver = self.profile_manager.setup_browser(profile_name)
            self.driver.get("https://www.google.com")
            
            print("\nBrowser opened with new profile.")
            print("Please log in to your desired website.")
            print("The profile will automatically save your session.")
            print("\nPress Enter when you're done...")
            input()
            
        except Exception as e:
            print(f"\nError creating profile: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
        
    def use_profile(self):
        """Handle using existing profile"""
        profiles = self.profile_manager.list_profiles()
        
        if not profiles:
            print("\nNo profiles found!")
            return
            
        print("\nAvailable profiles:")
        for idx, profile in enumerate(profiles, 1):
            last_used = profile['last_used'] or 'Never'
            print(f"{idx}. {profile['name']} (Created: {profile['created_at']}, Last used: {last_used})")
            
        while True:
            try:
                choice = int(input("\nSelect a profile number: "))
                if 1 <= choice <= len(profiles):
                    selected_profile = profiles[choice - 1]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
                
        try:
            self.driver = self.profile_manager.setup_browser(selected_profile['name'])
            self.driver.get("https://www.google.com")
            
            print(f"\nLoaded profile: {selected_profile['name']}")
            print("Press Enter to close the browser...")
            input()
            
        except Exception as e:
            print(f"\nError using profile: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
                
    def delete_profile(self):
        """Handle profile deletion"""
        profiles = self.profile_manager.list_profiles()
        
        if not profiles:
            print("\nNo profiles found!")
            return
            
        print("\nAvailable profiles:")
        for idx, profile in enumerate(profiles, 1):
            print(f"{idx}. {profile['name']} (Created: {profile['created_at']})")
            
        while True:
            try:
                choice = int(input("\nSelect a profile number to delete: "))
                if 1 <= choice <= len(profiles):
                    selected_profile = profiles[choice - 1]
                    break
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
                
        confirm = input(f"\nAre you sure you want to delete profile '{selected_profile['name']}'? (y/N): ").strip().lower()
        if confirm == 'y':
            try:
                self.profile_manager.delete_profile(selected_profile['name'])
                print(f"\nProfile '{selected_profile['name']}' deleted successfully.")
            except Exception as e:
                print(f"\nError deleting profile: {e}")
        else:
            print("\nDeletion cancelled.")
        
    def run(self):
        """Run the CLI application"""
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                self.create_profile()
            elif choice == "2":
                self.use_profile()
            elif choice == "3":
                self.delete_profile()
            elif choice == "4":
                profiles = self.profile_manager.list_profiles()
                if profiles:
                    print("\nAvailable profiles:")
                    for profile in profiles:
                        last_used = profile['last_used'] or 'Never'
                        print(f"- {profile['name']} (Created: {profile['created_at']}, Last used: {last_used})")
                else:
                    print("\nNo profiles found!")
            elif choice == "5":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please try again.") 