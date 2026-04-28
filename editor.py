import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from huffman import HuffmanCoding
from file_handler import read_text_file, write_text_file
from utils import format_compression_message


class TextEditorApp:
    """Tkinter-based text editor with multi-tab support and Huffman compression[cite: 13, 14]."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.huffman = HuffmanCoding()
        
        # Dictionary to track tab data: {tab_id: {"text_area": widget, "filepath": path}}
        self.tabs = {}
        
        self.is_dark_mode = False # Track the current theme state

        self.root.title("Basic Text Editor with Huffman Compression")
        self.root.geometry("1000x700")

        self._create_widgets()
        self._create_menu()
        self._create_status_bar()
        self._setup_bindings()
        
        # Start with one initial new file tab [cite: 21]
        self.new_file()

    def run(self) -> None:
        """Starts the main application loop."""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)
        self.root.mainloop()

    def _create_widgets(self) -> None:
        """Initializes the Notebook widget for multi-tab management[cite: 13]."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sync title bar with the active tab filename
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self._update_title())

    def _setup_bindings(self) -> None:
        """Standard keyboard shortcuts for editor operations."""
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-w>", lambda e: self.close_current_tab())

    def _get_current_tab_id(self) -> str:
        """Retrieves the ID of the active tab."""
        return self.notebook.select()

    def _get_current_data(self) -> dict:
        """Retrieves the text area and file path for the active tab."""
        tab_id = self._get_current_tab_id()
        return self.tabs.get(tab_id, {})

    def _create_menu(self) -> None:
        """Maintains the original menu structure[cite: 20, 24]."""
        menu_bar = tk.Menu(self.root)

        # File Menu [cite: 21, 23]
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Exit", command=self.exit_app)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit Menu [cite: 22]
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self._get_current_data()["text_area"].event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self._get_current_data()["text_area"].event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self._get_current_data()["text_area"].event_generate("<<Paste>>"))
        edit_menu.add_command(label="Select All", command=self.select_all)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # Compression Menu [cite: 24, 26, 27]
        compression_menu = tk.Menu(menu_bar, tearoff=0)
        compression_menu.add_command(label="Compress Saved File", command=self.compress_current_file)
        compression_menu.add_command(label="Decompress .huff File", command=self.decompress_file)
        menu_bar.add_cascade(label="Compression", menu=compression_menu)

        # Help Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _create_status_bar(self) -> None:
        self.status_frame = tk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(self.status_frame, textvariable=self.status_var, anchor="w")
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.theme_btn = tk.Button(self.status_frame, text="🌙 / ☀️", command=self.toggle_theme, relief=tk.FLAT, cursor="hand2")
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _update_title(self, event=None) -> None:
        data = self._get_current_data()
        if not data:
            self.root.title("Basic Text Editor with Huffman Compression")
            return
            
        filepath = data.get("filepath")
        filename = filepath if filepath else "Untitled"
        self.root.title(f"Basic Text Editor with Huffman Compression - {filename}")

    def _on_text_modified(self, text_widget: tk.Text) -> None:
        """Updates the status bar when the active buffer is changed."""
        if text_widget.edit_modified():
            self._set_status("Text modified")

    def _get_text_content(self, text_widget: tk.Text) -> str:
        return text_widget.get("1.0", tk.END + "-1c")

    def _add_new_tab(self, content: str = "", filepath: str = None) -> None:
        """Helper to create a new tab frame and text buffer[cite: 13, 21]."""
        tab_frame = tk.Frame(self.notebook)
        
        bg_color = "#2b2b2b" if getattr(self, 'is_dark_mode', False) else "white"
        fg_color = "#a9b7c6" if getattr(self, 'is_dark_mode', False) else "black"
        insert_bg = "white" if getattr(self, 'is_dark_mode', False) else "black"
        
        text_area = tk.Text(
            tab_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
            bg=bg_color,
            fg=fg_color,
            insertbackground=insert_bg
        )
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_area.insert(tk.END, content)
        
        # Reset the modified flag for new/opened content
        text_area.edit_modified(False)

        scrollbar = tk.Scrollbar(tab_frame, command=text_area.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.config(yscrollcommand=scrollbar.set)

        # Track modifications to trigger the "Save Changes" logic
        text_area.bind("<<Modified>>", lambda e: self._on_text_modified(text_area))

        tab_label = os.path.basename(filepath) if filepath else "Untitled"
        self.notebook.add(tab_frame, text=tab_label)
        
        tab_id = str(tab_frame)
        self.tabs[tab_id] = {"text_area": text_area, "filepath": filepath}
        self.notebook.select(tab_frame)

    def new_file(self) -> None:
        """Creates a fresh, untitled tab[cite: 21]."""
        self._add_new_tab()
        self._set_status("New file created")

    def open_file(self) -> None:
        """Opens a file, ensuring it is not already open in another tab[cite: 21]."""
        file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        # CONSISTENCY CHECK: Prevent duplicate tabs for the same disk file 
        for tab_id, data in self.tabs.items():
            if data["filepath"] == file_path:
                self.notebook.select(tab_id)
                self._set_status("File already open. Switched to existing tab.")
                return

        try:
            content = read_text_file(file_path)
            self._add_new_tab(content=content, filepath=file_path)
            self._set_status(f"Opened: {file_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to open file:\n{exc}")

    def save_file(self) -> bool:
        """Saves current tab content to disk[cite: 23]."""
        data = self._get_current_data()
        if not data: return False
        
        if data["filepath"] is None:
            return self.save_as_file()

        try:
            content = self._get_text_content(data["text_area"])
            write_text_file(data["filepath"], content)
            
            # Reset modification flag upon successfull save
            data["text_area"].edit_modified(False)
            
            self._update_title()
            self._set_status(f"Saved: {data['filepath']}")
            messagebox.showinfo("Success", "File saved successfully.")
            return True
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save file:\n{exc}")
            return False

    def save_as_file(self) -> bool:
        """Saves current content to a new path[cite: 23]."""
        data = self._get_current_data()
        if not data: return False

        file_path = filedialog.asksaveasfilename(
            title="Save Text File",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not file_path:
            return False

        try:
            content = self._get_text_content(data["text_area"])
            write_text_file(file_path, content)
            
            # Update tab metadata
            data["filepath"] = file_path
            data["text_area"].edit_modified(False)
            
            tab_id = self._get_current_tab_id()
            self.notebook.tab(tab_id, text=os.path.basename(file_path))
            
            self._update_title()
            self._set_status(f"Saved as: {file_path}")
            messagebox.showinfo("Success", "File saved successfully.")
            return True
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to save file:\n{exc}")
            return False

    def compress_current_file(self) -> None:
        """Runs Huffman compression on the saved disk file[cite: 24, 25, 26]."""
        data = self._get_current_data()
        if not data: return

        if data["filepath"] is None:
            messagebox.showwarning("Warning", "Please save the file first before compression.")
            return

        # Ensure the disk version matches the current UI buffer before compressing
        if not self.save_file():
            return

        default_name = os.path.splitext(os.path.basename(data["filepath"]))[0] + ".huff"
        output_path = filedialog.asksaveasfilename(
            title="Save Compressed File",
            initialfile=default_name,
            defaultextension=".huff",
            filetypes=[("Huffman Files", "*.huff"), ("All Files", "*.*")],
        )
        if not output_path:
            return

        try:
            result = self.huffman.compress_file(data["filepath"], output_path)
            self._set_status(f"Compressed to: {output_path}")
            messagebox.showinfo("Compression Complete", format_compression_message(result))
        except Exception as exc:
            messagebox.showerror("Compression Error", str(exc))

    def decompress_file(self) -> None:
        """Decompresses a .huff file back into text[cite: 27, 29]."""
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
                f"Decompression successful.\n\nRestored size: {result['restored_size']} bytes\n\nOpen restored file?",
            )
            if choice:
                content = read_text_file(output_path)
                self._add_new_tab(content=content, filepath=output_path)
        except Exception as exc:
            messagebox.showerror("Decompression Error", str(exc))

    def close_current_tab(self) -> None:
        """Closes the current tab with a modification check."""
        tab_id = self._get_current_tab_id()
        if not tab_id: return
        
        data = self.tabs[tab_id]
        if data["text_area"].edit_modified():
            filename = os.path.basename(data["filepath"]) if data["filepath"] else "Untitled"
            response = messagebox.askyesnocancel("Save Changes?", f"Save changes to {filename} before closing?")
            if response is True:
                if not self.save_file(): return
            elif response is None:
                return

        self.notebook.forget(tab_id)
        del self.tabs[tab_id]
        
        # Keep at least one tab open
        if not self.tabs:
            self.new_file()

    def select_all(self) -> None:
        data = self._get_current_data()
        if data:
            data["text_area"].tag_add(tk.SEL, "1.0", tk.END)

    def show_about(self) -> None:
        messagebox.showinfo("About", "Basic Text Editor with Huffman Compression\nCourse: CSE 323\nPlatform: Ubuntu/VMware [cite: 2, 3]")

    def toggle_theme(self) -> None:
        """Toggles between dark and light modes."""
        self.is_dark_mode = not self.is_dark_mode
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Applies the current theme colors to all text areas."""
        bg_color = "#2b2b2b" if self.is_dark_mode else "white"
        fg_color = "#a9b7c6" if self.is_dark_mode else "black"
        insert_bg = "white" if self.is_dark_mode else "black"

        for data in self.tabs.values():
            if "text_area" in data:
                data["text_area"].config(bg=bg_color, fg=fg_color, insertbackground=insert_bg)

    def exit_app(self) -> None:
        """Safe exit checking all tabs for unsaved modifications."""
        for tid in list(self.tabs.keys()):
            self.notebook.select(tid)
            if self.tabs[tid]["text_area"].edit_modified():
                self.close_current_tab()
                if tid in self.tabs: return # User cancelled
        self.root.destroy()