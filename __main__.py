# __main__.py
# Entry point for the Photo Sorter application.
# This file initializes the main controller and starts the Tkinter main loop.
# It exists to provide a clean, single entry for running the app as a script or module.

# --- Imports ---
from controller import PhotoSorterController

# --- Main Application Entry Point ---
def main():
    app = PhotoSorterController()
    app.view.mainloop()

# --- Script Execution Guard ---
if __name__ == "__main__":
    main()
