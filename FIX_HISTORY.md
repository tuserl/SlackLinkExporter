# Fix History & Technical Summary

## Issue Summary
When running the downloader script on extracted Slack export links, downloaded image and video files were saved as ~60 KB files instead of full-resolution binary media.

---

## Technical Root Cause Analysis

1. **Slack Export URL Types**:
   Slack export JSON files contain multiple URL fields for each file attachment:
   - `permalink` / `permalink_public`: Web app URLs (`https://<workspace>.slack.com/files/...`) pointing to Slack's HTML browser interface.
   - `url_private`: Viewer URL (`https://files.slack.com/files-pri/...`), which requires active browser session cookies; without them, Slack redirects to a **~60 KB HTML sign-in page**.
   - `url_private_download`: Direct binary media download URL (`https://files.slack.com/files-pri/.../download/...?token=xoxe-...`) containing the temporary download token parameter required to fetch the raw file directly.

2. **The Bug Workflow**:
   - `extract_urls.py` previously extracted all URL fields (`permalink`, `url_private`, `url_private_download`).
   - `downloader.py` processed URLs sequentially. It requested `url_private` or `permalink` first, received Slack's 60 KB HTML web page, and saved it to disk as e.g. `img_7266.jpg` (60 KB HTML file).
   - When `downloader.py` reached `url_private_download` for the same file, it saw `img_7266.jpg` already existed on disk, assumed it was already downloaded, and **skipped downloading the real media file**.

---

## Implemented Fixes

### 1. Direct Download URL Prioritization (`extract_urls.py`)
- Refactored `_walk()` in `extract_urls.py` to prioritize `url_private_download` (which contains the temporary token parameter `?token=xoxe-...`) for each file object.
- Excluded web app HTML permalinks (`permalink`, `permalink_public`) from URL extraction.

### 2. Content Validation & Stale File Cleanup (`downloader.py`)
- **Content-Type & Body Inspection**: Updated `download_file()` in `downloader.py` to verify HTTP `Content-Type` headers and inspect response body headers. HTML responses (`text/html` or `<!DOCTYPE`) are skipped and logged as warnings instead of being saved as media files.
- **Stale HTML Placeholder Removal**: When checking existing files on disk, `downloader.py` checks if the existing file starts with `<!DOCTYPE` or `<html`. Stale 60 KB HTML placeholder files are automatically deleted (`unlink()`) so the real binary media download can succeed.

### 3. Leaf Directory Targeting (`downloader.py`)
- Updated `download_all_in_directory()` to select only leaf channel directories containing `output.txt` (`leaf_outputs`), ensuring files are placed into their respective channel subfolders (`general`, `backend`, `frontend`, etc.).

---

## Verification & Results
- All 10 unit tests pass (`python -m unittest discover`).
- Extracted and downloaded 160+ full-sized images and videos across 22 Slack channel folders.
- Example downloaded file sizes:
  - `img_7268.png` → **9.95 MB**
  - `img_7266.jpg` → **6.71 MB**
  - `2026-06-22_19-38-21.mp4` → **22.6 MB**
  - `2026-06-22_15-11-05.mp4` → **16.1 MB**
  - `image.png` → **1.09 MB**
