"""
Photo Sorter Application Entry Point

This file serves as the main entry point for the Photo Sorter application.
Its primary purpose is to initialize the main controller, which sets up the application's logic and user interface, and then start the main event loop.
By centralizing the startup logic here, the application can be run both as a script and as a module, ensuring a single, clear entry for launching the app.
"""

# Import the main controller responsible for application logic and UI setup.
from controller import PhotoSorterController

# Define the main function that initializes the controller and starts the GUI event loop.
def main():
    app = PhotoSorterController()
    app.view.mainloop()

# Ensure the application starts only when this file is executed directly.
if __name__ == "__main__":
    main()
