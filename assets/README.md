# Assets Directory

This directory contains static assets and resources for the TikTok Clip Automator.

## Purpose

The assets folder is designed to store:
- Static files (images, icons, logos)
- Template files
- Configuration assets
- Resource files needed by the application
- Sample media files for testing

## Structure

Organize assets by type:
- `images/` - Image files (logos, icons, overlays)
- `fonts/` - Font files for text overlays
- `templates/` - Video templates and presets
- `audio/` - Sound effects and background music
- `samples/` - Sample input files for testing

## File Types

Common asset file types:
- Images: `.png`, `.jpg`, `.gif`, `.svg`
- Fonts: `.ttf`, `.otf`, `.woff`
- Audio: `.mp3`, `.wav`, `.aac`
- Video: `.mp4`, `.mov`, `.avi`
- Templates: `.json`, `.xml`

## Usage

Reference assets in your code:

```python
import os

# Get asset path
assets_dir = "assets"
logo_path = os.path.join(assets_dir, "images", "logo.png")
```

## Notes

- Keep assets organized in subdirectories
- Use descriptive filenames
- Optimize file sizes for performance
- Include attribution for third-party assets
