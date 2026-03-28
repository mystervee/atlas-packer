# Texture Atlas Builder

Texture Atlas Builder is a Python 3.12 desktop application (Tkinter + Pillow) for creating game-ready texture atlases.

## Features

- Atlas size presets and custom width/height.
- Import images from folder, file picker, or drag-and-drop (when `tkinterdnd2` is installed).
- Supported formats: PNG, JPG, TGA, WebP.
- Background options: transparent, black, white.
- Configurable border and padding.
- Packing modes:
  - Grid packing
  - Tight packing (simple shelf/bin-packing approach)
  - Fixed columns or rows
- Oversize handling:
  - Scale to fit
  - Reject with warning
  - Crop
- Live preview with zoom/pan and list-click highlighting.
- Validation summary (count, area, fill estimate, warnings).
- Export atlas: PNG, TGA, JPG, WebP.
- Optional metadata JSON export.

## Project Structure

```text
main.py
gui/
  main_window.py
  preview_canvas.py
  file_list_panel.py
  settings_panel.py
core/
  atlas_packer.py
  image_loader.py
  metadata_writer.py
utils/
  image_utils.py
  validation.py
```

## Requirements

- Python 3.12+
- Pillow
- Optional for drag-and-drop: `tkinterdnd2`

Install dependencies:

```bash
pip install pillow tkinterdnd2
```

(`tkinterdnd2` is optional; without it the app still works via file/folder dialogs.)

## Run

```bash
python main.py
```

## Metadata Example

```json
{
  "atlas": "atlas.png",
  "sprites": {
    "crate.png": { "x": 0, "y": 0, "w": 128, "h": 128 },
    "barrel.png": { "x": 128, "y": 0, "w": 128, "h": 128 }
  }
}
```
