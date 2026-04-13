import tkinter as tk
from editor import TextEditorApp


def main() -> None:
    root = tk.Tk()
    app = TextEditorApp(root)
    app.run()


if __name__ == "__main__":
    main()
