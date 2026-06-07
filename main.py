from gui import run_gui
from utils import fetch_access_keys


def main():
    access_keys = fetch_access_keys()
    run_gui(access_keys)


if __name__ == "__main__":
    main()
