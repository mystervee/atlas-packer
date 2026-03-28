"""File list UI for imported images and drag/drop support."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Callable

from core.image_loader import LoadedImage


class FileListPanel(ttk.Frame):
    """Panel that manages image import and displays loaded image metadata."""

    def __init__(
        self,
        master: tk.Widget,
        on_import_folder: Callable[[], None],
        on_import_files: Callable[[], None],
        on_drop_files: Callable[[list[str]], None],
        on_item_selected: Callable[[str], None],
    ) -> None:
        """Initialize file list widgets and event wiring."""
        super().__init__(master)
        self.on_import_folder = on_import_folder
        self.on_import_files = on_import_files
        self.on_drop_files = on_drop_files
        self.on_item_selected = on_item_selected
        self.tree = ttk.Treeview(self, columns=("name", "size"), show="headings", height=14)
        self._build()

    def _build(self) -> None:
        """Create import buttons and image treeview."""
        button_row = ttk.Frame(self)
        button_row.pack(fill="x", pady=(0, 6))

        ttk.Button(button_row, text="Import Folder", command=self.on_import_folder).pack(side="left", padx=(0, 6))
        ttk.Button(button_row, text="Import Files", command=self.on_import_files).pack(side="left")

        self.tree.heading("name", text="Filename")
        self.tree.heading("size", text="Dimensions")
        self.tree.column("name", width=220)
        self.tree.column("size", width=120, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        ttk.Label(
            self,
            text="Tip: Drag and drop files here (when tkinterdnd2 is installed).",
            foreground="#666666",
        ).pack(anchor="w", pady=(6, 0))

    def populate(self, images: list[LoadedImage]) -> None:
        """Refresh displayed image rows."""
        self.tree.delete(*self.tree.get_children())
        for item in images:
            self.tree.insert("", "end", iid=item.name, values=(item.name, f"{item.width} x {item.height}"))

    def attach_drop_support(self, dnd_files_token: str | None) -> None:
        """Enable drop target if TK DnD token is available."""
        if not dnd_files_token:
            return

        self.tree.drop_target_register(dnd_files_token)
        self.tree.dnd_bind("<<Drop>>", self._on_drop)

    def _on_drop(self, event: tk.Event) -> None:
        """Handle dropped file paths and forward to import callback."""
        file_paths = [str(Path(path)) for path in self.tk.splitlist(event.data)]
        if file_paths:
            self.on_drop_files(file_paths)

    def _on_tree_select(self, _event: tk.Event) -> None:
        """Forward selected image name for preview highlighting."""
        selected = self.tree.selection()
        if selected:
            self.on_item_selected(selected[0])


def ask_folder() -> str | None:
    """Show folder selection dialog."""
    return filedialog.askdirectory(title="Select image folder") or None


def ask_files() -> tuple[str, ...]:
    """Show file selection dialog for supported image types."""
    return filedialog.askopenfilenames(
        title="Select image files",
        filetypes=[
            ("Images", "*.png *.jpg *.jpeg *.tga *.webp"),
            ("All files", "*.*"),
        ],
    )
