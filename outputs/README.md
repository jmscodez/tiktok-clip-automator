# Outputs Directory

This directory contains the generated output files from the TikTok Clip Automator.

## Purpose

The outputs folder is the destination for:
- Generated TikTok clips
- Processed video files
- Exported content
- Batch processing results
- Final rendered videos

## Structure

Organize outputs by type and date:
- `videos/` - Final video output files
- `clips/` - Individual clip segments
- `thumbnails/` - Generated thumbnail images
- `metadata/` - Output metadata and logs
- `batch_[YYYY-MM-DD]/` - Date-stamped batch results

## File Naming Convention

Recommended naming patterns:
- Videos: `tiktok_clip_[timestamp]_[id].mp4`
- Thumbnails: `thumb_[timestamp]_[id].jpg`
- Batch folders: `batch_2025-08-20_[session]`

## File Formats

Typical output formats:
- Videos: `.mp4`, `.mov`, `.webm`
- Images: `.jpg`, `.png`, `.gif`
- Metadata: `.json`, `.txt`, `.csv`
- Logs: `.log`

## Usage

The application will automatically create subdirectories and files in this location:

```python
import os
from datetime import datetime

# Generate output path
output_dir = "outputs"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"tiktok_clip_{timestamp}.mp4"
output_path = os.path.join(output_dir, "videos", output_file)
```

## Notes

- Files are automatically organized by the application
- Check disk space regularly for large video outputs
- Consider archiving old outputs periodically
- This folder may be excluded from version control
