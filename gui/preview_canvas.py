"""Zoomable preview canvas for atlas visualization and highlighting."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from core.atlas_packer import SpritePlacement


class PreviewCanvas(ttk.Frame):
    """Widget that renders atlas image with pan/zoom controls."""

    def __init__(self, master: tk.Widget) -> None:
        """Initialize canvas and interaction bindings."""
        super().__init__(master)

        toolbar = ttk.Frame(self)
        toolbar.pack(side="top", fill="x")
        ttk.Button(toolbar, text="Fit", command=self._reset_zoom).pack(side="left")

        self._canvas_frame = ttk.Frame(self)
        self._canvas_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self._canvas_frame, background="#1f1f1f", width=600, height=600)
        self.canvas.place(relx=0.5, rely=0.5, anchor="center")

        self._zoom = 1.0
        self._base_image: Image.Image | None = None
        self._photo: ImageTk.PhotoImage | None = None
        self._placements: dict[str, SpritePlacement] = {}
        self._image_id: int | None = None
        self._highlight_id: int | None = None
        self._selected_sprite: str | None = None
        self._render_job: str | None = None

        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas_frame.bind("<Configure>", self._on_frame_resize)

    def set_image(
        self, image: Image.Image, placements: dict[str, SpritePlacement]
    ) -> None:
        """Load new atlas image and sprite placements into preview."""
        self._base_image = image
        self._placements = placements
        self._zoom = self._fit_zoom()
        self._render()

    def highlight(self, sprite_name: str) -> None:
        """Highlight a placement rectangle for selected sprite name."""
        self._selected_sprite = sprite_name

        if self._highlight_id is not None:
            self.canvas.delete(self._highlight_id)
            self._highlight_id = None

        if not sprite_name:
            return

        placement = self._placements.get(sprite_name)
        if not placement:
            return

        z = self._zoom
        self._highlight_id = self.canvas.create_rectangle(
            placement.x * z,
            placement.y * z,
            (placement.x + placement.width) * z,
            (placement.y + placement.height) * z,
            outline="#ff4040",
            width=2,
        )

    def _reset_zoom(self) -> None:
        """Reset zoom to fit the full image within the canvas."""
        self._zoom = self._fit_zoom()
        self._render()

    def _fit_zoom(self) -> float:
        """Return zoom level that fits the full image within the current canvas."""
        if self._base_image is None:
            return 1.0
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return 1.0
        return min(cw / self._base_image.width, ch / self._base_image.height)

    @staticmethod
    def _make_checkerboard(width: int, height: int, tile: int = 16) -> Image.Image:
        """Return an RGBA checkerboard image of the given pixel dimensions."""
        tile2 = tile * 2
        cell = Image.new("RGBA", (tile2, tile2))
        cell.paste((204, 204, 204, 255), (0,    0,    tile,  tile))   # light top-left
        cell.paste((153, 153, 153, 255), (tile, 0,    tile2, tile))   # dark  top-right
        cell.paste((153, 153, 153, 255), (0,    tile, tile,  tile2))  # dark  bottom-left
        cell.paste((204, 204, 204, 255), (tile, tile, tile2, tile2))  # light bottom-right
        bg = Image.new("RGBA", (width, height))
        for y in range(0, height, tile2):
            for x in range(0, width, tile2):
                bg.paste(cell, (x, y))
        return bg

    def _schedule_render(self) -> None:
        """Schedule rendering with debounce to prevent UI freezing."""
        if self._render_job is not None:
            self.after_cancel(self._render_job)
        # 50ms delay is usually enough to batch fast wheel scroll events
        self._render_job = self.after(50, self._render)

    def _on_frame_resize(self, event: tk.Event) -> None:
        """Enforce square canvas by sizing to the smaller frame dimension."""
        size = min(event.width, event.height)
        self.canvas.configure(width=size, height=size)
        # Canvas Configure event fires next, scheduling re-render via _on_canvas_resize

    def _on_canvas_resize(self, event: tk.Event) -> None:
        """Handle canvas resize to update rendering region."""
        self._schedule_render()

    def _render(self) -> None:
        """Render atlas image according to current zoom value using a visible viewport optimization."""
        self._render_job = None

        if self._base_image is None:
            self.canvas.delete("all")
            return

        total_w = max(1, int(self._base_image.width * self._zoom))
        total_h = max(1, int(self._base_image.height * self._zoom))

        # Get the visible region of the canvas in scaled coordinates
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw <= 1 or ch <= 1:
            # Not fully initialized, reschedule rendering
            self._schedule_render()
            return

        cx = self.canvas.canvasx(0)
        cy = self.canvas.canvasy(0)

        # Add a buffer (0.5x canvas dimensions) to avoid pan flicker while keeping resize cost low
        buffer_x = cw // 2
        buffer_y = ch // 2

        left = max(0, cx - buffer_x)
        top = max(0, cy - buffer_y)
        right = min(total_w, cx + cw + buffer_x)
        bottom = min(total_h, cy + ch + buffer_y)

        # Convert back to original image coordinates for cropping
        orig_left = int(left / self._zoom)
        orig_top = int(top / self._zoom)
        orig_right = int(right / self._zoom)
        orig_bottom = int(bottom / self._zoom)

        # Ensure we don't try to crop an invalid 0x0 area
        if orig_right <= orig_left or orig_bottom <= orig_top:
            return

        # Crop the image first
        cropped = self._base_image.crop((orig_left, orig_top, orig_right, orig_bottom))

        # Resize only the cropped region
        target_w = int((orig_right - orig_left) * self._zoom)
        target_h = int((orig_bottom - orig_top) * self._zoom)

        # Guard against zero dimension due to floating point precision
        if target_w <= 0 or target_h <= 0:
            return

        resized = cropped.resize((target_w, target_h), Image.Resampling.NEAREST)

        # Composite over checkerboard if the image has an alpha channel
        if resized.mode == "RGBA":
            display = Image.alpha_composite(
                self._make_checkerboard(target_w, target_h), resized
            )
        else:
            display = resized

        self._photo = ImageTk.PhotoImage(display)

        self.canvas.delete("all")

        # Place the image at the scaled 'left, top' coordinates we derived
        # We need to map 'orig_left, orig_top' precisely back to scaled coords
        # so it lines up with the full logical scrollregion.
        render_x = int(orig_left * self._zoom)
        render_y = int(orig_top * self._zoom)

        self._image_id = self.canvas.create_image(
            render_x, render_y, anchor="nw", image=self._photo
        )
        self.canvas.config(scrollregion=(0, 0, total_w, total_h))

        # Redraw highlight if any
        if self._selected_sprite is not None:
            self.highlight(self._selected_sprite)

    def _on_zoom(self, event: tk.Event) -> None:
        """Adjust zoom by mouse wheel movement."""
        if event.delta > 0:
            self._zoom = min(8.0, self._zoom * 1.1)
        else:
            self._zoom = max(0.1, self._zoom / 1.1)
        self._schedule_render()

    def _on_pan_start(self, event: tk.Event) -> None:
        """Start drag pan operation."""
        self.canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event: tk.Event) -> None:
        """Apply drag pan operation and schedule render to show newly revealed areas."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self._schedule_render()
