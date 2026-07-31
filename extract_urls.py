import json
from pathlib import Path
from typing import Any


IMAGE_KEYS = {
    "url_private",
    "url_private_download",
    "permalink",
    "permalink_public",
}


def _walk(obj: Any, urls: set[str]) -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if (
                key in IMAGE_KEYS
                and isinstance(value, str)
                and value.startswith("http")
            ):
                urls.add(value)

            _walk(value, urls)

    elif isinstance(obj, list):
        for item in obj:
            _walk(item, urls)


def extract_image_urls(json_file: str | Path) -> set[str]:
    """
    Extract all unique image URLs from a JSON file.
    """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls: set[str] = set()
    _walk(data, urls)
    return urls


def export_urls(json_file: str | Path, output_file: str | Path = "output.txt") -> int:
    """
    Export unique URLs to output.txt.

    Returns:
        Number of URLs written.
    """
    urls = sorted(extract_image_urls(json_file))

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(urls))

    return len(urls)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("python extract_urls.py file.json")
        raise SystemExit(1)

    count = export_urls(sys.argv[1])
    print(f"Exported {count} unique URLs.")
