import json
import tempfile
import unittest
from pathlib import Path

from extract_urls import extract_image_urls, export_urls


class TestExtractURLs(unittest.TestCase):

    def test_extract_unique_urls(self):
        data = {
            "files": [
                {
                    "url_private": "https://a.com/image1.jpg",
                    "url_private_download": "https://a.com/image1.jpg",
                },
                {
                    "url_private": "https://a.com/image2.jpg",
                },
            ]
        }

        with tempfile.TemporaryDirectory() as d:
            json_path = Path(d) / "test.json"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            urls = extract_image_urls(json_path)

            self.assertEqual(
                urls,
                {
                    "https://a.com/image1.jpg",
                    "https://a.com/image2.jpg",
                },
            )

    def test_export(self):
        data = {
            "files": [
                {
                    "permalink": "https://a.com/abc.jpg"
                }
            ]
        }

        with tempfile.TemporaryDirectory() as d:
            json_path = Path(d) / "sample.json"
            output = Path(d) / "output.txt"

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            count = export_urls(json_path, output)

            self.assertEqual(count, 1)
            self.assertTrue(output.exists())
            self.assertIn("https://a.com/abc.jpg", output.read_text())


if __name__ == "__main__":
    unittest.main()
