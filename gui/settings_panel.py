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

    def _add_combobox_row(
        self, row: int, label_text: str, variable: tk.Variable, values: list[str], width: int = 15, sticky: str = "ew"
    ) -> None:
        """Add a row with a label and a combobox."""
        ttk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(self, textvariable=variable, values=values, state="readonly", width=width).grid(
            row=row, column=1, sticky=sticky, padx=6, pady=4
        )

    def _add_entry_row(self, row: int, label_text: str, variable: tk.Variable, width: int = 10) -> None:
        """Add a row with a label and an entry."""
        ttk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(self, textvariable=variable, width=width).grid(row=row, column=1, sticky="ew", padx=6, pady=4)

    def _add_spinbox_row(
        self, row: int, label_text: str, variable: tk.Variable, from_: int, to: int, width: int = 8, sticky: str = "w"
    ) -> None:
        """Add a row with a label and a spinbox."""
        ttk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(self, from_=from_, to=to, textvariable=variable, width=width).grid(
            row=row, column=1, sticky=sticky, padx=6, pady=4
        )

    def _add_radio_group_row(self, row: int, label_text: str, variable: tk.Variable, options: list[str]) -> None:
        """Add a row with a label and a group of radio buttons."""
        ttk.Label(self, text=label_text).grid(row=row, column=0, sticky="w", padx=6, pady=4)
        frame = ttk.Frame(self)
        frame.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        for option in options:
            ttk.Radiobutton(frame, text=option, value=option, variable=variable).pack(side="left")

    def _build(self) -> None:
        """Lay out all setting controls in a compact form."""
        row = 0
        self._add_combobox_row(row, "Atlas Preset:", self.preset_var, self.PRESETS)

        row += 1
        self._add_entry_row(row, "Custom Width:", self.custom_w_var)

        row += 1
        self._add_entry_row(row, "Custom Height:", self.custom_h_var)

        row += 1
        self._add_radio_group_row(row, "Background:", self.background_var, ["Transparent", "Black", "White"])

        row += 1
        self._add_spinbox_row(row, "Outer Border:", self.border_var, 0, 256)

        row += 1
        self._add_spinbox_row(row, "Padding:", self.padding_var, 0, 256)

        row += 1
        self._add_combobox_row(
            row,
            "Packing Mode:",
            self.packing_mode_var,
            ["Grid packing", "Tight packing", "Fixed columns or rows"],
            width=20,
        )

        row += 1
        ttk.Label(self, text="Fixed Layout:").grid(row=row, column=0, sticky="w", padx=6, pady=4)
        fixed_frame = ttk.Frame(self)
        fixed_frame.grid(row=row, column=1, sticky="w", padx=6, pady=4)
        ttk.Radiobutton(fixed_frame, text="Columns", value="columns", variable=self.fixed_mode_var).pack(side="left")
        ttk.Radiobutton(fixed_frame, text="Rows", value="rows", variable=self.fixed_mode_var).pack(side="left")
        ttk.Spinbox(fixed_frame, from_=1, to=256, textvariable=self.fixed_value_var, width=5).pack(side="left", padx=(6, 0))

        row += 1
        self._add_radio_group_row(
            row, "Oversize Rule:", self.oversize_rule_var, ["Scale to fit", "Reject with warning", "Crop"]
        )

        row += 1
        self._add_combobox_row(
            row, "Export Format:", self.export_format_var, ["PNG", "TGA", "JPG", "WEBP"], width=8, sticky="w"
        )

        row += 1
        ttk.Checkbutton(self, text="Export metadata JSON", variable=self.export_metadata_var).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=6, pady=4
        )

        self.columnconfigure(1, weight=1)

    def get_settings(self) -> dict[str, object]:
        """Collect typed settings values from controls."""
        return {
            "preset": self.preset_var.get(),
            "custom_w": self.custom_w_var.get(),
            "custom_h": self.custom_h_var.get(),
            "background": self.background_var.get(),
            "border": int(self.border_var.get() or 0),
            "padding": int(self.padding_var.get() or 0),
            "packing_mode": self.packing_mode_var.get(),
            "fixed_mode": self.fixed_mode_var.get(),
            "fixed_value": int(self.fixed_value_var.get() or 1),
            "oversize_rule": self.oversize_rule_var.get(),
            "export_metadata": bool(self.export_metadata_var.get()),
            "export_format": self.export_format_var.get(),
        }
