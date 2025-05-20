# __main__.py
# Entry point for the Photo Sorter application.
# This file initializes the main controller and starts the Tkinter main loop.
# It exists to provide a clean, single entry for running the app as a script or module.

from controller import PhotoSorterController


def main():
    app = PhotoSorterController()
    app.view.mainloop()


if __name__ == "__main__":
    main()
