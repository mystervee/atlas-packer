"""Main application window and orchestration for Texture Atlas Builder."""

from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.atlas_packer import AtlasPacker, PackResult
from core.image_loader import ImageLoader, LoadedImage
from core.metadata_writer import write_metadata_json
from gui.file_list_panel import FileListPanel, ask_files, ask_folder
from gui.preview_canvas import PreviewCanvas
from gui.settings_panel import SettingsPanel
from utils.image_utils import parse_atlas_size
from utils.validation import ValidationSummary, build_validation_summary


class MainWindow:
    """Top-level GUI controller for image import, packing, preview, and export."""

    def __init__(self, root: tk.Tk, dnd_files_token: str | None = None) -> None:
        """Initialize app state, services, and main layout."""
        self.root = root
        self.root.title("Texture Atlas Builder")
        self.root.geometry("1320x760")

        self.loader = ImageLoader()
        self.packer = AtlasPacker()

        self.images: list[LoadedImage] = []
        self.last_result: PackResult | None = None

        self._build(dnd_files_token)

    def _build(self, dnd_files_token: str | None) -> None:
        """Build and place child panels and action controls."""
        root_frame = ttk.Frame(self.root, padding=8)
        root_frame.pack(fill="both", expand=True)

        left = ttk.Frame(root_frame)
        left.pack(side="left", fill="y")

        self.file_panel = FileListPanel(
            left,
            on_import_folder=self.import_folder,
            on_import_files=self.import_files,
            on_drop_files=self.import_file_paths,
            on_item_selected=self.on_item_selected,
        )
        self.file_panel.pack(fill="both", expand=True)
        self.file_panel.attach_drop_support(dnd_files_token)

        self.settings = SettingsPanel(left)
        self.settings.pack(fill="x", pady=(10, 0))

        action_row = ttk.Frame(left)
        action_row.pack(fill="x", pady=(10, 0))
        ttk.Button(action_row, text="Validate", command=self.validate).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="Pack Preview", command=self.pack_preview).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="Export Atlas", command=self.export).pack(side="left")

        self.validation_text = tk.Text(left, height=8, width=54)
        self.validation_text.pack(fill="x", pady=(10, 0))

        self.preview = PreviewCanvas(root_frame)
        self.preview.pack(side="left", fill="both", expand=True, padx=(8, 0))

    def import_folder(self) -> None:
        """Import all images from a selected folder."""
        folder = ask_folder()
        if not folder:
            return
        loaded = self.loader.load_from_folder(folder)
        self._merge_images(loaded)

    def import_files(self) -> None:
        """Import selected image files."""
        files = ask_files()
        if not files:
            return
        self.import_file_paths(list(files))

    def import_file_paths(self, files: list[str]) -> None:
        """Import files from explicit paths (file dialog or drag/drop)."""
        loaded = self.loader.load_from_files(files)
        self._merge_images(loaded)

    def _merge_images(self, loaded: list[LoadedImage]) -> None:
        """Merge newly loaded images by name, replacing duplicates."""
        existing = {img.name: img for img in self.images}
        for img in loaded:
            existing[img.name] = img
        self.images = sorted(existing.values(), key=lambda img: img.name.lower())
        self.file_panel.populate(self.images)

    def _get_atlas_size(self) -> tuple[int, int]:
        """Resolve atlas width/height from settings fields."""
        values = self.settings.get_settings()
        return parse_atlas_size(str(values["preset"]), str(values["custom_w"]), str(values["custom_h"]))

    def validate(self) -> None:
        """Run and display pre-pack validation summary."""
        if not self.images:
            messagebox.showinfo("No Images", "Please import one or more images first.")
            return

        values = self.settings.get_settings()
        summary = build_validation_summary(
            self.images,
            self._get_atlas_size(),
            values["border"],
            values["padding"],
        )
        self._show_validation_summary(summary)

    def _show_validation_summary(self, summary: ValidationSummary) -> None:
        """Render validation summary and warning text."""
        lines = [
            f"Images: {summary.image_count}",
            f"Total pixel area: {summary.total_pixel_area:,}",
            f"Atlas pixel area: {summary.atlas_pixel_area:,}",
            f"Estimated fill: {summary.estimated_fill_percent:.2f}%",
        ]
        if summary.warnings:
            lines.append("Warnings:")
            lines.extend(f"- {warning}" for warning in summary.warnings)

        self.validation_text.delete("1.0", "end")
        self.validation_text.insert("1.0", "\n".join(lines))

    def pack_preview(self) -> None:
        """Pack images in background thread and update preview when done."""
        if not self.images:
            messagebox.showinfo("No Images", "Please import one or more images first.")
            return

        values = self.settings.get_settings()

        def worker() -> None:
            try:
                result = self.packer.pack(
                    self.images,
                    self._get_atlas_size(),
                    str(values["packing_mode"]),
                    values["border"],
                    values["padding"],
                    str(values["background"]),
                    str(values["oversize_rule"]),
                    str(values["fixed_mode"]),
                    values["fixed_value"],
                )
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: messagebox.showerror("Packing Error", str(exc)))
                return

            self.root.after(0, lambda: self._on_pack_done(result))

        threading.Thread(target=worker, daemon=True).start()

    def _on_pack_done(self, result: PackResult) -> None:
        """Store pack result, render preview, and surface warnings."""
        self.last_result = result
        self.preview.set_image(result.atlas, result.placements)

        warnings = "\n".join(result.warnings) if result.warnings else "No warnings"
        self.validation_text.delete("1.0", "end")
        self.validation_text.insert(
            "1.0",
            f"Packed sprites: {len(result.placements)}\nFill percentage: {result.fill_percent:.2f}%\n\n{warnings}",
        )

    def on_item_selected(self, item_name: str) -> None:
        """Highlight selected file position in preview."""
        self.preview.highlight(item_name)

    def export(self) -> None:
        """Export atlas image and optional metadata JSON."""
        if self.last_result is None:
            self.pack_preview()
            messagebox.showinfo("Packing Started", "Packing started in background. Export again when preview updates.")
            return

        values = self.settings.get_settings()
        fmt = str(values["export_format"]).upper()
        ext = "jpg" if fmt == "JPG" else fmt.lower()

        save_path = filedialog.asksaveasfilename(
            title="Save Atlas",
            defaultextension=f".{ext}",
            filetypes=[
                ("PNG", "*.png"),
                ("TGA", "*.tga"),
                ("JPEG", "*.jpg"),
                ("WebP", "*.webp"),
            ],
        )
        if not save_path:
            return

        atlas = self.last_result.atlas
        if fmt == "JPG":
            atlas = atlas.convert("RGB")

        pil_fmt = "JPEG" if fmt == "JPG" else fmt
        atlas.save(save_path, format=pil_fmt)

        if bool(values["export_metadata"]):
            metadata_path = Path(save_path).with_suffix(".json")
            write_metadata_json(metadata_path, Path(save_path).name, self.last_result.placements)

        messagebox.showinfo("Export Complete", f"Atlas exported to:\n{save_path}")


def launch_app() -> None:
    """Create app root window and start Tkinter loop."""
    dnd_files_token: str | None = None

    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD

        root = TkinterDnD.Tk()
        dnd_files_token = DND_FILES
    except Exception:  # noqa: BLE001
        root = tk.Tk()

    MainWindow(root, dnd_files_token=dnd_files_token)
    root.mainloop()
