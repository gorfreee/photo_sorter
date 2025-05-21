"""
__main__.py
Entry point for the Photo Sorter application.
This file initializes the main controller and starts the DearPyGui main loop.
"""

from controller import PhotoSorterController


def main():
    app = PhotoSorterController()
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
