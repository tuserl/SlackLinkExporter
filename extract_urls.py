import json
from pathlib import Path
from typing import Any


IMAGE_KEYS = {
    "url_private_download",
    "url_private",
}



def _walk(obj: Any, urls: set[str]) -> None:
    if isinstance(obj, dict):
        if (
            "url_private_download" in obj
            and isinstance(obj["url_private_download"], str)
            and obj["url_private_download"].startswith("http")
        ):
            urls.add(obj["url_private_download"])
        elif (
            "url_private" in obj
            and isinstance(obj["url_private"], str)
            and obj["url_private"].startswith("http")
        ):
            urls.add(obj["url_private"])
        else:
            for value in obj.values():
                _walk(value, urls)

    elif isinstance(obj, list):
        for item in obj:
            _walk(item, urls)



from scanner import find_json_files


def extract_image_urls(target_path: str | Path) -> set[str]:
    """
    Extract all unique image URLs from a JSON file or recursively from a directory of JSON files.
    """
    path = Path(target_path)
    if path.is_dir():
        urls: set[str] = set()
        for json_file in find_json_files(path):
            urls.update(extract_image_urls(json_file))
        return urls

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    urls: set[str] = set()
    _walk(data, urls)
    return urls


def export_urls(
    target_path: str | Path,
    output_file: str | Path = "output.txt",
    split_by_folder: bool = True,
) -> int:
    """
    Export unique URLs from a JSON file or directory to output.txt.
    If target_path is a directory and split_by_folder is True, exports an output.txt
    inside each subfolder containing JSON files before merging them into the main output file.

    Returns:
        Number of unique URLs written to the main output file.
    """
    path = Path(target_path)
    output_path = Path(output_file)

    if not path.is_dir():
        urls = sorted(extract_image_urls(path))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(urls))
        return len(urls)

    json_files = find_json_files(path)
    folder_map: dict[Path, set[str]] = {}
    all_urls: set[str] = set()

    for json_file in json_files:
        folder = json_file.parent.resolve()
        if folder not in folder_map:
            folder_map[folder] = set()

        file_urls = extract_image_urls(json_file)
        folder_map[folder].update(file_urls)
        all_urls.update(file_urls)

    if split_by_folder:
        output_filename = output_path.name
        for folder, folder_urls in folder_map.items():
            folder_output = folder / output_filename
            with open(folder_output, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(folder_urls)))

    sorted_all_urls = sorted(all_urls)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted_all_urls))

    return len(sorted_all_urls)



if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("python extract_urls.py <file.json | directory>")
        raise SystemExit(1)

    count = export_urls(sys.argv[1])
    print(f"Exported {count} unique URLs.")

