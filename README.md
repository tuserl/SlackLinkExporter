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
├── downloader.py
├── test_scanner.py
├── test_extract_urls.py
├── test_downloader.py
├── FIX_HISTORY.md
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

A file named `output.txt` will be created.

---

## 2. Recursively search all JSON files in a directory and export image URLs

To recursively scan a folder for all `.json` files, create a separate `output.txt` inside each folder containing JSON files, and export all merged image URLs to the main `output.txt`:

```bash
python extract_urls.py ./slack_export
```

Or to search the current directory and all subdirectories:

```bash
python extract_urls.py .
```

Output

```
Exported 150 unique URLs.
```

- Each subfolder containing JSON files will get an `output.txt` with URLs extracted from that specific folder.
- A main `output.txt` containing all deduplicated image URLs across all subfolders will be created at the specified output path.


---

## 3. Auto-download all files to their respective parent folders

To automatically download all extracted files from `output.txt` into each corresponding subfolder:

```bash
python downloader.py ./slack_export
```

Or to download files from a single `output.txt` file into its containing directory:

```bash
python downloader.py ./slack_export/general/output.txt
```

### Optional: Private Slack Token

If your Slack export URLs require private authentication headers (`url_private` or `url_private_download`), pass your token as a command-line argument or set the `SLACK_TOKEN` environment variable:

```bash
python downloader.py ./slack_export xoxb-your-slack-token
```

Or set the environment variable:

```bash
export SLACK_TOKEN="xoxb-your-slack-token"
python downloader.py ./slack_export
```

Output:

```
Downloading files from slack_export/general/output.txt...
Downloaded 15 file(s) into slack_export/general
Downloading files from slack_export/backend/output.txt...
Downloaded 30 file(s) into slack_export/backend

Completed: Downloaded 45 file(s) across 2 folder(s).
```

---

## 4. Use as a Python module

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

Run only the downloader tests:

```bash
python -m unittest test_downloader.py
```

Expected output

```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.03s

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

### `extract_image_urls(target_path)`

Extracts all unique image URLs from a single Slack export JSON file or recursively from a directory of JSON files.

Returns

```python
set[str]
```

---

### `export_urls(target_path, output_file="output.txt", split_by_folder=True)`

Extracts all unique image URLs from a single JSON file or recursively from a directory of JSON files. When `target_path` is a directory and `split_by_folder` is `True`, an `output.txt` is created inside each subfolder containing JSON files before merging all URLs into the top-level `output_file`.

Returns

```python
int
```

The total number of unique URLs exported to the main output file.

---

## downloader.py

### `download_all_in_directory(root_dir, token=None)`

Recursively finds all `output.txt` files under `root_dir` and downloads all files into their respective parent folders.

Returns

```python
dict[pathlib.Path, list[pathlib.Path]]
```

### `download_urls_from_file(output_file, token=None)`

Reads URLs line-by-line from `output_file` and downloads each file into the directory containing `output_file`.

Returns

```python
list[pathlib.Path]
```



---

# Notes

- Duplicate URLs are automatically removed.
- URLs are sorted before being written to the output file.
- The project uses only Python's standard library.
- Designed for Slack export JSON files but can be extended to support other JSON formats.
