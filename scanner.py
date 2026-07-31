from pathlib import Path
import sys


def find_json_files(root: str) -> list[Path]:
    """
    Recursively find every .json file under root.
    """
    return sorted(Path(root).rglob("*.json"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("python scanner.py <directory>")
        raise SystemExit(1)

    json_files = find_json_files(sys.argv[1])

    print(f"Found {len(json_files)} JSON file(s):")

    for file in json_files:
        print(file)
