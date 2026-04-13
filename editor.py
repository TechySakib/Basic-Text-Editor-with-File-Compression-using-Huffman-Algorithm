import os
import tkinter as tk
from tkinter import filedialog, messagebox

from huffman import HuffmanCoding
from file_handler import read_text_file, write_text_file
from utils import format_compression_message


class TextEditorApp:
    """Tkinter-based text editor integrated with Huffman compression."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.current_file: str | None = None
        self.huffman = HuffmanCoding()

        self.root.title("Basic Text Editor with Huffman Compression")
        self.root.geometry("1000x700")

        self._create_widgets()
        self._create_menu()
        self._create_status_bar()
        self._update_title()

    def run(self) -> None:
        self.root.mainloop()

    def _create_widgets(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(
            frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(frame, command=self.text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        self.text_area.bind("<<Modified>>", self._on_text_modified)

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Select All", command=self.select_all)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        compression_menu = tk.Menu(menu_bar, tearoff=0)
        compression_menu.add_command(label="Compress Saved File", command=self.compress_current_file)
        compression_menu.add_command(label="Decompress .huff File", command=self.decompress_file)
        menu_bar.add_cascade(label="Compression", menu=compression_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _create_status_bar(self) -> None:
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, anchor="w", relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _update_title(self) -> None:
        filename = self.current_file if self.current_file else "Untitled"
        self.root.title(f"Basic Text Editor with Huffman Compression - {filename}")

    def _on_text_modified(self, event=None) -> None:
        self.text_area.edit_modified(False)
        self._set_status("Text modified")

    def _get_text_content(self) -> str:
        return self.text_area.get("1.0", tk.END + "-1c")

    def new_file(self) -> None:
        if self._confirm_discard_unsaved_changes():
            self.text_area.delete("1.0", tk.END)
            self.current_file = None
            self._update_title()
            self._set_status("New file created")

    def open_file(self) -> None:
        if not self._confirm_discard_unsaved_changes():
            return

        file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        try:
            content = read_text_file(file_path)
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.current_file = file_path
            self._update_title()
            self._set_status(f"Opened: {file_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to open file:\n{exc}")

    def save_file(self) -> bool:
        if self.current_file is None:
            return self.save_as_file()

        try:
            write_text_file(self.current_file, self._get_text_content())
            self._update_title()
            self._set_status(f"Saved: {self.current_file}")
            messagebox.showinfo("Success", "File saved successfully.")
            return True
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save file:\n{exc}")
            return False

    def save_as_file(self) -> bool:
        file_path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return False

        try:
            write_text_file(file_path, self._get_text_content())
            self.current_file = file_path
            self._update_title()
            self._set_status(f"Saved as: {file_path}")
            messagebox.showinfo("Success", "File saved successfully.")
            return True
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save file:\n{exc}")
            return False

    def compress_current_file(self) -> None:
        if self.current_file is None:
            messagebox.showwarning("Warning", "Please save the file first before compression.")
            return

        if not self.save_file():
            return

        default_name = os.path.splitext(os.path.basename(self.current_file))[0] + ".huff"
        output_path = filedialog.asksaveasfilename(
            title="Save Compressed File",
            initialfile=default_name,
            defaultextension=".huff",
            filetypes=[("Huffman Files", "*.huff"), ("All Files", "*.*")],
        )
        if not output_path:
            return

        try:
            result = self.huffman.compress_file(self.current_file, output_path)
            self._set_status(f"Compressed to: {output_path}")
            messagebox.showinfo("Compression Complete", format_compression_message(result))
        except Exception as exc:
            messagebox.showerror("Compression Error", str(exc))

    def decompress_file(self) -> None:
        input_path = filedialog.askopenfilename(
            title="Open Compressed File",
            filetypes=[("Huffman Files", "*.huff"), ("All Files", "*.*")],
        )
        if not input_path:
            return

        suggested_name = os.path.splitext(os.path.basename(input_path))[0] + "_restored.txt"
        output_path = filedialog.asksaveasfilename(
            title="Save Restored Text File",
            initialfile=suggested_name,
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not output_path:
            return

        try:
            result = self.huffman.decompress_file(input_path, output_path)
            self._set_status(f"Decompressed to: {output_path}")

            choice = messagebox.askyesno(
                "Decompression Complete",
                f"Decompression successful.\n\nRestored size: {result['restored_size']} bytes\n\nOpen the restored file in the editor?",
            )
            if choice:
                content = read_text_file(output_path)
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert(tk.END, content)
                self.current_file = output_path
                self._update_title()
                self._set_status(f"Opened restored file: {output_path}")
        except Exception as exc:
            messagebox.showerror("Decompression Error", str(exc))

    def _confirm_discard_unsaved_changes(self) -> bool:
        content = self._get_text_content().strip()
        if content:
            return messagebox.askyesno(
                "Confirm",
                "Current editor content may be lost.\nDo you want to continue?",
            )
        return True

    def select_all(self) -> None:
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def show_about(self) -> None:
        messagebox.showinfo(
            "About",
            "Basic Text Editor with Huffman Compression using Python\n\n"
            "Features:\n"
            "- New / Open / Save / Save As\n"
            "- Huffman Compression\n"
            "- Huffman Decompression\n"
            "- Tkinter GUI\n"
            "- Multi-file clean project structure",
        )

    def exit_app(self) -> None:
        if self._confirm_discard_unsaved_changes():
            self.root.destroy()
