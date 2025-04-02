from tkinter import Tk
from src.ui.ui import UI


def main():
    window = Tk()
    window.title("Pef-laskuri")

    ui_view = UI(window)
    ui_view.start()

    window.mainloop()


if __name__ == "__main__":
    main()
