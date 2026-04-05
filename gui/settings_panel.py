"""Settings panel UI for atlas and packing options."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class SettingsPanel(ttk.LabelFrame):
    """Form controls that gather atlas generation settings."""

    PRESETS = ["256x256", "512x512", "1024x1024", "2048x2048", "4096x4096", "8192x8192", "Custom"]

    def __init__(self, master: tk.Widget) -> None:
        """Create all setting widgets and default values."""
        super().__init__(master, text="Settings")
        self.preset_var = tk.StringVar(value="1024x1024")
        self.custom_w_var = tk.StringVar(value="1024")
        self.custom_h_var = tk.StringVar(value="1024")
        self.background_var = tk.StringVar(value="Transparent")
        self.border_var = tk.StringVar(value="0")
        self.padding_var = tk.StringVar(value="2")
        self.packing_mode_var = tk.StringVar(value="Tight packing")
        self.fixed_mode_var = tk.StringVar(value="columns")
        self.fixed_value_var = tk.StringVar(value="4")
        self.oversize_rule_var = tk.StringVar(value="Scale to fit")
        self.export_metadata_var = tk.BooleanVar(value=True)
        self.export_format_var = tk.StringVar(value="PNG")

        self._build()

    def _build(self) -> None:
        """Lay out all setting controls in a compact form."""
        row = 0
        ttk.Label(self, text="Atlas Preset:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(self, textvariable=self.preset_var, values=self.PRESETS, state="readonly", width=15).grid(
            row=row, column=1, sticky="ew", padx=6, pady=4
        )

        row += 1
        ttk.Label(self, text="Custom Width:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(self, textvariable=self.custom_w_var, width=10).grid(row=row, column=1, sticky="ew", padx=6, pady=4)

        row += 1
        ttk.Label(self, text="Custom Height:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(self, textvariable=self.custom_h_var, width=10).grid(row=row, column=1, sticky="ew", padx=6, pady=4)

        row += 1
        ttk.Label(self, text="Background:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        bg_row = ttk.Frame(self)
        bg_row.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        for text in ("Transparent", "Black", "White"):
            ttk.Radiobutton(bg_row, text=text, value=text, variable=self.background_var).pack(side="left")

        row += 1
        ttk.Label(self, text="Outer Border:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(self, from_=0, to=256, textvariable=self.border_var, width=8).grid(
            row=row, column=1, sticky="w", padx=6, pady=4
        )

        row += 1
        ttk.Label(self, text="Padding:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(self, from_=0, to=256, textvariable=self.padding_var, width=8).grid(
            row=row, column=1, sticky="w", padx=6, pady=4
        )

        row += 1
        ttk.Label(self, text="Packing Mode:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            self,
            textvariable=self.packing_mode_var,
            values=["Grid packing", "Tight packing", "Fixed columns or rows"],
            state="readonly",
            width=20,
        ).grid(row=row, column=1, sticky="ew", padx=6, pady=4)

        row += 1
        ttk.Label(self, text="Fixed Layout:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        fixed_frame = ttk.Frame(self)
        fixed_frame.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        ttk.Radiobutton(fixed_frame, text="Columns", value="columns", variable=self.fixed_mode_var).pack(side="left")
        ttk.Radiobutton(fixed_frame, text="Rows", value="rows", variable=self.fixed_mode_var).pack(side="left")
        ttk.Spinbox(fixed_frame, from_=1, to=256, textvariable=self.fixed_value_var, width=5).pack(side="left", padx=(6, 0))

        row += 1
        ttk.Label(self, text="Oversize Rule:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        over_frame = ttk.Frame(self)
        over_frame.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        ttk.Radiobutton(over_frame, text="Scale to fit", value="Scale to fit", variable=self.oversize_rule_var).pack(side="left")
        ttk.Radiobutton(
            over_frame,
            text="Reject with warning",
            value="Reject with warning",
            variable=self.oversize_rule_var,
        ).pack(side="left")
        ttk.Radiobutton(over_frame, text="Crop", value="Crop", variable=self.oversize_rule_var).pack(side="left")

        row += 1
        ttk.Label(self, text="Export Format:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            self,
            textvariable=self.export_format_var,
            values=["PNG", "TGA", "JPG", "WEBP"],
            state="readonly",
            width=8,
        ).grid(row=row, column=1, sticky="w", padx=6, pady=4)

        row += 1
        ttk.Checkbutton(self, text="Export metadata JSON", variable=self.export_metadata_var).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=4
        )

        self.columnconfigure(1, weight=1)

    def _int_or_default(self, value: str, default: int) -> int:
        """Safely convert string to int with a fallback."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def get_settings(self) -> dict[str, object]:
        """Collect typed settings values from controls."""
        return {
            "preset": self.preset_var.get(),
            "custom_w": self.custom_w_var.get(),
            "custom_h": self.custom_h_var.get(),
            "background": self.background_var.get(),
            "border": self._int_or_default(self.border_var.get(), 0),
            "padding": self._int_or_default(self.padding_var.get(), 0),
            "packing_mode": self.packing_mode_var.get(),
            "fixed_mode": self.fixed_mode_var.get(),
            "fixed_value": self._int_or_default(self.fixed_value_var.get(), 1),
            "oversize_rule": self.oversize_rule_var.get(),
            "export_metadata": bool(self.export_metadata_var.get()),
            "export_format": self.export_format_var.get(),
        }
