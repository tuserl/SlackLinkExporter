# Slack Image URL Extractor

A simple Python utility for:

- Recursively scanning a folder for Slack export JSON files
- Extracting all image URLs
- Removing duplicate URLs
- Exporting the result to `output.txt`

---

## Project Structure

```text
project/
│
├── scanner.py
├── extract_urls.py
├── test_scanner.py
├── test_extract_urls.py
└── README.md
```

---

# Requirements

- Python 3.10+

No third-party packages are required.

---

# Usage

## 1. Extract URLs from a single JSON file

```bash
python extract_urls.py messages.json
```

Example

```bash
python extract_urls.py "Pasted code.json"
```

Output

```
Exported 53 unique URLs.
```

A file named

```
output.txt
```

will be created.

---

## 2. Use as a Python module

```python
from extract_urls import extract_image_urls

urls = extract_image_urls("messages.json")

print(len(urls))

for url in urls:
    print(url)
```

Export directly:

```python
from extract_urls import export_urls

count = export_urls(
    "messages.json",
    "output.txt"
)

print(count)
```

---

# Recursively Find JSON Files

```python
from scanner import find_json_files

json_files = find_json_files("./slack_export")

for file in json_files:
    print(file)
```

Example output

```
slack_export/general/2026-07-01.json
slack_export/general/2026-07-02.json
slack_export/random/2026-07-03.json
```

---

# Process an Entire Slack Export

```python
from scanner import find_json_files
from extract_urls import extract_image_urls

all_urls = set()

for json_file in find_json_files("./slack_export"):
    all_urls.update(
        extract_image_urls(json_file)
    )

with open("output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(all_urls)))

print(f"Found {len(all_urls)} unique image URLs.")
```

This scans every JSON file under `./slack_export` and writes one deduplicated `output.txt`.

---

# Running Unit Tests

Run every test:

```bash
python -m unittest discover
```

Run only the scanner tests:

```bash
python -m unittest test_scanner.py
```

Run only the URL extraction tests:

```bash
python -m unittest test_extract_urls.py
```

Expected output

```
..
----------------------------------------------------------------------
Ran 2 tests in 0.01s

OK
```

---

# Functions

## scanner.py

### `find_json_files(root)`

Recursively finds every `.json` file under the specified directory.

Returns

```python
list[pathlib.Path]
```

---

## extract_urls.py

### `extract_image_urls(json_file)`

Extracts all unique image URLs from a Slack export JSON file.

Returns

```python
set[str]
```

---

### `export_urls(json_file, output_file="output.txt")`

Extracts all unique image URLs and writes them to an output text file.

Returns

```python
int
```

The number of unique URLs exported.

---

# Notes

- Duplicate URLs are automatically removed.
- URLs are sorted before being written to the output file.
- The project uses only Python's standard library.
- Designed for Slack export JSON files but can be extended to support other JSON formats.
