# Utils Directory

This directory contains utility functions and helper modules for the TikTok Clip Automator.

## Purpose

The utils folder is designed to house:
- Common utility functions
- Helper classes
- Shared constants and configurations
- Utility modules for specific tasks

## Structure

As the project grows, you can organize utilities into subdirectories:
- `video_utils.py` - Video processing utilities
- `file_utils.py` - File handling utilities
- `api_utils.py` - API interaction utilities
- `config_utils.py` - Configuration management utilities

## Usage

Import utilities in your main application:

```python
from utils.video_utils import process_video
from utils.file_utils import ensure_directory_exists
```

## Notes

- Keep utility functions pure and reusable
- Add proper documentation for each utility
- Write tests for utility functions
