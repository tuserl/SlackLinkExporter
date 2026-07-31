import os
from pathlib import Path
import re
import sys
import urllib.parse
import urllib.request
from typing import Optional


def get_filename_from_url(url: str) -> str:
    """
    Extract a safe filename from a URL.
    """
    parsed = urllib.parse.urlparse(url)
    filename = Path(parsed.path).name
    if not filename or filename.startswith("."):
        filename = f"file_{hash(url) & 0xFFFFFFFF:08x}.bin"

    # Remove unsafe filesystem characters
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename



def download_file(
    url: str,
    output_dir: str | Path,
    token: Optional[str] = None,
    timeout: int = 15,
) -> Optional[Path]:
    """
    Download a single file from URL to output_dir.
    Returns the Path of downloaded file, or None if failed.
    """
    dest_dir = Path(output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    filename = get_filename_from_url(url)
    dest_path = dest_dir / filename

    # Skip if file already exists, is non-empty, and is a valid binary (not an HTML error page)
    if dest_path.exists() and dest_path.stat().st_size > 0:
        try:
            with open(dest_path, "rb") as f:
                head = f.read(512).lower()
                if b"<!doctype" in head or b"<html" in head:
                    dest_path.unlink()
                else:
                    return dest_path
        except OSError:
            pass

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" in content_type:
                print(
                    f"Warning: {url} returned HTML content (Content-Type: {content_type}). "
                    "Skipping saving HTML as media. Ensure URL is valid and Slack token is provided if required.",
                    file=sys.stderr,
                )
                return None

            data = response.read()
            head = data[:512].lower()
            if b"<!doctype" in head or b"<html" in head:
                print(
                    f"Warning: {url} response body starts with HTML markup. Skipping.",
                    file=sys.stderr,
                )
                return None

            with open(dest_path, "wb") as out_file:
                out_file.write(data)

        return dest_path
    except Exception as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
        if dest_path.exists():
            try:
                dest_path.unlink()
            except OSError:
                pass
        return None



def download_urls_from_file(
    output_file: str | Path,
    token: Optional[str] = None,
) -> list[Path]:
    """
    Read URLs from output_file and download all files into output_file's parent directory.
    """
    file_path = Path(output_file)
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return []

    target_dir = file_path.parent
    urls = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and line.strip().startswith("http")
    ]

    downloaded: list[Path] = []
    for url in urls:
        res = download_file(url, target_dir, token=token)
        if res:
            downloaded.append(res)

    return downloaded


def download_all_in_directory(
    root_dir: str | Path,
    token: Optional[str] = None,
) -> dict[Path, list[Path]]:
    """
    Recursively find leaf output.txt files in root_dir and download their files into their respective folders.
    """
    root = Path(root_dir)
    results: dict[Path, list[Path]] = {}

    if root.is_file():
        downloaded = download_urls_from_file(root, token=token)
        results[root.parent] = downloaded
        return results

    # Find all output.txt files recursively
    all_output_files = set(root.rglob("output.txt"))

    # A file is a leaf output.txt if no other output.txt resides in a subdirectory below it
    leaf_outputs = [
        f
        for f in all_output_files
        if not any(
            other != f and other.is_relative_to(f.parent)
            for other in all_output_files
        )
    ]

    for output_file in sorted(leaf_outputs):
        print(f"Downloading files from {output_file}...")
        downloaded = download_urls_from_file(output_file, token=token)
        results[output_file.parent] = downloaded
        print(f"Downloaded {len(downloaded)} file(s) into {output_file.parent}")

    return results



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python downloader.py <directory | output.txt> [slack_token]")
        sys.exit(1)

    target_arg = sys.argv[1]
    slack_token = sys.argv[2] if len(sys.argv) > 2 else os.getenv("SLACK_TOKEN")

    res = download_all_in_directory(target_arg, token=slack_token)
    total_files = sum(len(files) for files in res.values())
    print(f"\nCompleted: Downloaded {total_files} file(s) across {len(res)} folder(s).")
