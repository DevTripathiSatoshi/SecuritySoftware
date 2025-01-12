from TaskManager import ThirdPartySoftwareDetector
from colorama import Fore, Style
import json

class LocalDatabase:
    def __init__(self):
        self.database = []

    def fetch_and_store_data(self):
        """
        Fetch third-party software data and store it locally.
        """
        detector = ThirdPartySoftwareDetector()
        self.database = detector.fetch_data()

    def print_database(self):
        """
        Print the local database with color coding.
        """
        print(f"\n{'='*40}\nLocal Third-Party Software Database\n{'='*40}\n")
        for idx, app in enumerate(self.database, start=1):
            print(
                f"[{Fore.CYAN}#{idx}{Style.RESET_ALL}] "
                f"Name: {Fore.BLUE}{app['Name']}{Style.RESET_ALL}, "
                f"User: {Fore.YELLOW if app['None_User'] else Fore.RED}{app['User'] or 'None'}{Style.RESET_ALL}, "
                f"Path: {Fore.GREEN}{app['Path']}{Style.RESET_ALL}, "
                f"PIDs: {Fore.YELLOW if app['Multiple_PIDs'] else Style.RESET_ALL}{', '.join(map(str, app['PIDs']))}{Style.RESET_ALL}, "
                f"Multiple PIDs: {app['Multiple_PIDs']}, "
                f"None User: {app['None_User']}"
            )

    def save_to_file(self, filename="local_database.json"):
        """
        Save the local database to a file.
        """
        with open(filename, 'w') as f:
            json.dump(self.database, f, indent=4)
        print(f"\n{Fore.GREEN}Database saved to {filename}{Style.RESET_ALL}.")


if __name__ == "__main__":
    # Create the local database instance
    local_db = LocalDatabase()
    
    # Fetch and store data
    local_db.fetch_and_store_data()
    
    # Print the database
    local_db.print_database()
    
    # Save to a file
    local_db.save_to_file()
