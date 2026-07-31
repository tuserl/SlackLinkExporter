from pathlib import Path


def find_json_files(root: str) -> list[Path]:
    """
    Recursively find every .json file under root.
    """
    return sorted(Path(root).rglob("*.json"))
